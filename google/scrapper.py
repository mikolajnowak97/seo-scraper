from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from urllib.parse import unquote
from decimal import Decimal

import chromedriver_autoinstaller
import re

from google.selectors import Selectors
from database import DatabaseConnection
from database.models import GoogleMapsRecord


class GoogleMapsScrapper():

    def __init__(self):
        print("Chromedriver Installing")
        driver_path = chromedriver_autoinstaller.install()

        print("Chrome Browser Opening")
        options = Options()
        options.add_argument("--incognito")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.selectors = Selectors()

    def __open_google_maps(self):

        endpoint = f'https://www.google.com/maps/search/{self.searchphrase}/?hl=pl'
        endpoint = re.sub(r'\s{1,}', '+', endpoint)

        print(f'Opening: {endpoint}')
        self.driver.get(endpoint)

        if 'consent.google.com' in self.driver.current_url:
            print('Closing Google Policies')
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, self.selectors.xpath_google_accept_all)))
            self.driver.find_element(By.XPATH, self.selectors.xpath_google_accept_all).click()
            print('Closed Google Policies')

    def __collect_data(self):

        def check_end():
            try:
                results_grid.find_element(By.CSS_SELECTOR, self.selectors.css_results_end)
            except NoSuchElementException:
                return False
            return True


        print('Fetching data from google maps...')
        results_grid = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, self.selectors.css_results)))
        
        end_reached = False
        while not end_reached:
            results_grid.send_keys(Keys.END)
            end_reached = check_end()
            # break

        self.results = results_grid.find_elements(By.CSS_SELECTOR, self.selectors.css_results_item)
        print(f'Fetched {len(self.results)} records')

    def __process_data(self):
        def find_displayname():
            return record.find_element(By.CSS_SELECTOR, self.selectors.css_results_item_full_name).text
        def find_place_url():
            return record.find_element(By.CSS_SELECTOR, self.selectors.css_results_item_place_url).get_attribute("href")
        def find_rating():
            try:
                return Decimal(record.find_element(By.CSS_SELECTOR, self.selectors.css_results_item_rating).text.replace(',','.'))
            except NoSuchElementException:
                    return None
        def find_reviews():
            try:
                return int(record.find_element(By.CSS_SELECTOR, self.selectors.css_results_item_reviews).text.replace('(','').replace(')',''))
            except NoSuchElementException:
                return 0
        def find_website():
            try:
                return record.find_element(By.CSS_SELECTOR, self.selectors.css_results_item_website).get_attribute("href")
            except NoSuchElementException:
                return None            
        def find_description():
            try:
                description = record.find_element(By.CSS_SELECTOR, self.selectors.css_results_item_description).text
                try:
                    return description.replace(gmr.phone, '')
                except TypeError:
                    return description
            except NoSuchElementException:
                return None
        def find_phone():
            try:
                return record.find_element(By.CSS_SELECTOR, self.selectors.css_results_item_phone).text
            except NoSuchElementException:
                return None
        def find_category():
            try:
                return record.find_element(By.CSS_SELECTOR, self.selectors.css_results_item_category_street).text.split('·')[0]
            except NoSuchElementException:
                return None
        def find_street():
            try:
                return record.find_element(By.CSS_SELECTOR, self.selectors.css_results_item_category_street).text.split('·')[1].strip()
            except (NoSuchElementException, IndexError):
                return None
        def find_latitude():
            url = unquote(gmr.place_url)
            match = re.search('(?<=!3d)(.*)(?=!4d)', url)
            return match.group(0)
        def find_longitude():
            url = unquote(gmr.place_url)
            match = re.search('(?<=!4d)(.*)(?=!16s)', url)
            return match.group(0)

        print('Processing data...')
        i = 1
        for record in self.results:
            gmr = GoogleMapsRecord(self.connection)
            gmr.searchphrase = self.searchphrase
            gmr.displayname = find_displayname()
            gmr.place_url = find_place_url()
            gmr.lat = find_latitude()
            gmr.lng = find_longitude()
            gmr.category = find_category()
            gmr.street = find_street()
            gmr.phone = find_phone()
            gmr.website = find_website()
            gmr.description = find_description()
            gmr.rating = find_rating()
            gmr.reviews = find_reviews()
            gmr.search_order = i
            i = i + 1

            if not gmr.exists():
                gmr.insert()

        print('All data processed!')

    def scrap(self, searchphrase):
        database = DatabaseConnection()
        self.connection = database.connection

        self.searchphrase = searchphrase
        self.__open_google_maps()
        self.__collect_data()
        self.__process_data()

        self.connection.commit()
        self.connection.close()

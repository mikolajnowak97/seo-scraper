from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
import requests, json, re

from database import DatabaseConnection
from website.models import Website


class WebsiteScraper:

    def __init__(self):
        database = DatabaseConnection()
        self.connection = database.connection

    def __pagespeed_test__(self, website):

        def __get_data(strategy):
            def __process_data__():
                setattr(website, f"ps_{strategy.lower()}_timing_total", site_json["lighthouseResult"]["timing"]["total"])
                setattr(website, f"ps_{strategy.lower()}_score_seo", site_json["lighthouseResult"]["categories"]["seo"]["score"])
                setattr(website, f"ps_{strategy.lower()}_score_performance", site_json["lighthouseResult"]["categories"]["performance"]["score"])
                setattr(website, f"ps_{strategy.lower()}_score_accessibility", site_json["lighthouseResult"]["categories"]["accessibility"]["score"])
                setattr(website, f"ps_{strategy.lower()}_score_best_practices", site_json["lighthouseResult"]["categories"]["best-practices"]["score"])

            key = "AIzaSyCA3Z1SzaTTAOr5magopxwFSBaHV3us6CQ"
            url = f"https://pagespeedonline.googleapis.com/pagespeedonline/v5/runPagespeed?key={key}&url={website.requested_url}&strategy={strategy.upper()}&category=PERFORMANCE&category=ACCESSIBILITY&category=BEST_PRACTICES&category=SEO"
            response = requests.get(url)
            if response.ok:
                site_json=json.loads(response.text)
                __process_data__()

        __get_data('DESKTOP')
        __get_data('MOBILE')

    def exit(self):
        self.connection.close()

    def scrap(self, url):
        def find_meta_title():
            title = soup.find("title")
            return title.string if title else None
        def find_meta_robots():
            robots = soup.find("meta", attrs={"name": "robots"})
            return robots["content"] if robots else None
        def find_meta_canonical():
            canonical = soup.find("link", attrs={"rel": "canonical"})
            return canonical["href"] if canonical else None
        def find_meta_description():
            description = soup.find("meta", attrs={"name": "description"})
            return description["content"] if description else None
        def find_has_googleanalytics():
            gtag = soup.find("script", src=re.compile("/gtag/"))
            return gtag is not None
        def find_h1():
            all_h1 = soup.find_all("h1")
            if all_h1:
                h1s = []
                for h1 in all_h1:
                    h1s.append(h1.text)
                return json.dumps(h1s, ensure_ascii=False)
            
            else:
                return None
        def find_h2():
            all_h2 = soup.find_all("h2")
            if all_h2:
                h2s = []
                for h2 in all_h2:
                    h2s.append(h2.text)
                return json.dumps(h2s, ensure_ascii=False)
            
            else:
                return None
        
        print("Checking: " + url)        
        website = Website(url)
        try:
            response = requests.get(url)
            website.status_code = response.status_code
            website.is_accessible = response.ok
        except ConnectionError:
            website.is_accessible = False
            website.status_code = 500

        if website.is_accessible:
            soup = BeautifulSoup(response.content, "html.parser")
            website.is_secure = "https://" in response.url
            website.status_code = response.status_code
            website.destination_url = response.url

            if not website.is_secure:
                try:
                    url_secure = url.replace("http://", "https://")
                    response = requests.get(url_secure)
                    soup = BeautifulSoup(response.content, "html.parser")
                    website.destination_url = url_secure
                    website.status_code = response.status_code
                    website.is_secure = True
                except ConnectionError:
                    pass

            website.meta_title = find_meta_title()
            website.meta_robots = find_meta_robots()
            website.meta_canonical = find_meta_canonical()
            website.meta_description = find_meta_description()
            website.has_googleanalytics = find_has_googleanalytics()
            website.h1s = find_h1()
            website.h2s = find_h2()

            self.__pagespeed_test__(website)
            
        website.insert(self.connection)

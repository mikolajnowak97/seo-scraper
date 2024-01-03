from website.scraper import WebsiteScraper


urls = []

bss = WebsiteScraper()
for url in urls:
    bss.scrap(url)

bss.exit()

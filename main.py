from google.scraper import GoogleMapsScraper

search_phrases = [
    "pokoje gościnne darłówko",
    "domki darłówko",
    "darłówko domki",
    "pokoje darłówko",
    "noclegi darłówko",
    "kwatery darłówko",
    "darłowo domki",
    "noclegi darłowo",
]

gms = GoogleMapsScraper()
for search_phrase in search_phrases:
    gms.scrap(search_phrase)

gms.connection.close()

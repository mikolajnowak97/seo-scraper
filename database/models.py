from psycopg2.extras import RealDictCursor

class GoogleMapsRecord():

    def __init__(self, connection):
        self.connection = connection

    def __repr__(self):
        return repr(self.full_name)

    def exists(self):
        cur = self.connection.cursor(cursor_factory=RealDictCursor)
        cur.execute(f"SELECT EXISTS(SELECT 1 FROM public.googlemaps WHERE search_phrase='{self.search_phrase}' AND displayname='{self.displayname}' AND search_order={self.search_order})")
        record = cur.fetchone()
        cur.close()
        return record['exists']
    
    def insert(self):
        cur = self.connection.cursor()
        cur.execute("""
                    INSERT INTO public.googlemaps(uuid, search_phrase, search_url, search_order, displayname, place_url, category, street, phone, website, description, icon_url, rating, reviews, lat, lng)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
                    (self.uuid, self.search_phrase, self.search_url, self.search_order, self.displayname, self.place_url, self.category, self.street, self.phone, self.website, self.description, self.icon_url, self.rating, self.reviews, self.lat, self.lng))
        cur.close()
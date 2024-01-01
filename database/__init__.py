import psycopg2


class DatabaseConnection:

    def __init__(self):
        print('Connecting to the PostgreSQL database...')
        self.connection = psycopg2.connect(
            database="seo-scrapper",
            host="localhost",
            port="5432",
            user="postgres",
            password="admin123",
        )
		
        # create a cursor
        cur = self.connection.cursor()
        
        # execute a statement
        cur.execute('SELECT version()')
        db_version = cur.fetchone()
        print('PostgreSQL database version: ' + str(db_version))
        
        # close the communication with the PostgreSQL
        cur.close()

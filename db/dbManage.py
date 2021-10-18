import sqlite3
import requests

class DBManager():
    def __init__(self, db):
        self.db = db
        self.con = None
        self.cur = None
        self.create_connection()
    
    def create_connection(self):
        self.con = sqlite3.connect(self.db, check_same_thread=False)
        self.cur = self.con.cursor()
        self.execute_query("CREATE TABLE IF NOT EXISTS Users (deezerID int PRIMARY KEY UNIQUE,name text,email text, token text, lastMix timestamp, playlist int);")
        self.execute_query("CREATE TABLE IF NOT EXISTS Artistes (id_artiste integer PRIMARY KEY UNIQUE,name text);")
        self.execute_query("CREATE TABLE IF NOT EXISTS Genres (id_genre integer PRIMARY KEY UNIQUE,name text);")
        self.execute_query("CREATE TABLE IF NOT EXISTS Albums (id_album integer PRIMARY KEY UNIQUE,name text);")
        self.execute_query("CREATE TABLE IF NOT EXISTS TracksUser (deezerID integer,track_id int, FOREIGN KEY (track_id) REFERENCES Tracks (track_id));")
        self.execute_query("CREATE TABLE IF NOT EXISTS Tracks (track_id int PRIMARY KEY UNIQUE,id_album int,id_genre int,id_artiste int,score int,duration int, bpm int, title text, FOREIGN KEY (id_artiste) REFERENCES Artistes (id_artiste), FOREIGN KEY (id_album) REFERENCES Albums (id_album), FOREIGN KEY (id_genre) REFERENCES Genres (id_genre));")
        self.execute_query("CREATE TABLE IF NOT EXISTS Daily (deezerID integer,track_id int, FOREIGN KEY (track_id) REFERENCES Tracks (track_id));")
        
        data = []

        r = requests.get('https://api.deezer.com/genre')
        
        for i in r.json()['data']:
            data.append((i['id'],i['name']))

        self.cur.executemany('INSERT OR REPLACE INTO Genres(id_genre,name) VALUES (?,?)', data)

        self.con.commit()

    def execute_query(self, query,data=()):
        self.cur.execute(query, data)
        self.con.commit()

    def executemany(self, query,data=()):
        self.cur.executemany(query, data)
        self.con.commit()

    def execute_read_query(self, query,data=()):
        result = None
        self.cur.execute(query, data)
        result = self.cur.fetchall()
        return result

        


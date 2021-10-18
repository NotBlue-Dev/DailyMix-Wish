from flask import *
from config import *
import requests
from config import *

from datetime import datetime
from routes.generate import newMixPage

process = Blueprint('process', __name__, template_folder='templates')

# # # # # # # # # 
# 
# # # # # # # # # 

@process.route("/process", methods=['GET', 'POST'])
def processPage():
    try:
        r = requests.get('https://api.deezer.com/user/me/tracks?limit=2000', {'access_token': session["token"]})
        code = r.json()['error']['code']
        if code == 300:
            return redirect('/token')
    except:
        pass

    session['loaded'] = True

    if request.method == 'GET':
        return render_template('loading.html')

    if request.method == 'POST':
        r = requests.get('https://api.deezer.com/user/me/tracks?limit=2000', {'access_token': session["token"]})

        # GET ALL TRACKS DATA (Artists, album, genres, bpm, tracks etc)
        datasTracks = []
        datasAlbum = []
        datasArtist = []
        datasTrackUser = []

        try:
            userid = DBManaging.execute_read_query("SELECT deezerID FROM Users WHERE deezerID = ?", (session["deezerID"],))[0][0]
        except:
            return {"code":"token"}

        for i in r.json()["data"]:
            # IF NOT IN DB SEARCH DATA
            if len(DBManaging.execute_read_query('SELECT track_id FROM TracksUser WHERE track_id = ? and deezerID = ?', (i["id"],userid))) == 0:
                
                datasArtist.append((i['artist']['id'],i['artist']['name']))
                datasAlbum.append((i['album']['id'], i['album']['title']))
                
                try:
                    tracks = requests.get(f'https://api.deezer.com/track/{i["id"]}').json()

                    bpm = tracks["bpm"]
                    if bpm == 0:
                        bpm = None
                    duration = tracks["duration"]
                except:
                    bpm = None

                try:
                    genre = requests.get(f'https://api.deezer.com/album/{i["album"]["id"]}').json()["genre_id"]
                    if genre == -1:
                        genre = None
                except:
                    genre = None
                datasTracks.append((i["id"], i['album']['id'],genre, i['artist']['id'], i['rank'], duration, bpm, i['title']))
                datasTrackUser.append((userid,i['id']))
                
        DBManaging.executemany("INSERT OR REPLACE INTO Albums (id_album, name) VALUES (?,?)", datasAlbum)
        DBManaging.executemany("INSERT OR REPLACE INTO Artistes (id_artiste, name) VALUES (?,?)", datasArtist)
        DBManaging.executemany("INSERT OR REPLACE INTO Tracks (track_id, id_album, id_genre, id_artiste, score, duration, bpm, title) VALUES (?,?,?,?,?,?,?,?)", datasTracks)
        DBManaging.executemany("INSERT OR REPLACE INTO TracksUser (deezerID, track_id) VALUES (?,?)", datasTrackUser)

        # if 24h has passed, create new mix
        now = datetime.now()
        data = DBManaging.execute_read_query("SELECT lastMix FROM Users WHERE deezerID = ?", (session["deezerID"],))[0][0]

        if data == None:
            newMixPage()
        else:
            last = datetime.strptime(data, "%Y-%m-%d %H:%M:%S.%f")
            tot = now - last
            if tot.seconds > 86400:
                newMixPage()

        return {"code":"done"}
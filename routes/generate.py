from flask import Blueprint, redirect, session
from flask.globals import request
from config import *
from datetime import datetime
import pandas as pd  
from sklearn.ensemble import RandomForestRegressor
import requests
from random import *
newMix = Blueprint('newMix', __name__, template_folder='templates')

# # # # # # # # # 
# GENERATE DAILY MIX
# # # # # # # # # 

@newMix.route('/newMix', methods=['POST'])
def newMixPage():
    if request.method == 'POST':
        #  create dataframe

        # clear last daily mix
        DBManaging.execute_query('DELETE FROM Daily WHERE deezerID = ?', (session["deezerID"],))

        userid = DBManaging.execute_read_query("SELECT deezerID FROM Users WHERE deezerID = ?", (session["deezerID"],))[0][0]
        data = {'trackID': [], 'albumID': [], 'genre': [], 'artistID': [], 'rank': [], 'duration': [], 'bpm': []}  
        dataDB = DBManaging.execute_read_query('SELECT * FROM TracksUser INNER JOIN Tracks ON Tracks.track_id = TracksUser.track_id WHERE TracksUser.deezerID =?', (userid,))
        for i in dataDB:
            if not None in i:
                data['trackID'].append(i[1])
                data['albumID'].append(i[3])
                data['genre'].append(i[4])
                data['artistID'].append(i[5])
                data['rank'].append(i[6])
                data['duration'].append(i[7])
                data['bpm'].append(i[8])
        df = pd.DataFrame(data) 

        # SICKIT LEARN
        # genre,album,artist,bpm,duration

        columns = df.columns.tolist()
        columns = [c for c in columns if c not in ["trackID", "rank"]]
        
        def predict(targ, nb):
            model = RandomForestRegressor(n_estimators=200, min_samples_leaf=1, random_state=50)

            model.fit(df[columns], df[targ])

            predictions = model.predict(df[columns])

            if targ == 'duration':
                predictions = [round(num) for num in model.predict(df[columns])]
                
            return predictions[:nb]

        # NORMAL:
        # 40% Discovery artiste (related) FAIT
        # 100 % use bpm/dur prediction FAIT
        # 30 % track from your most listened artist FAIT 
        # 30 % track from your most listened album FAIT 

        # DISCOVERY:
        # 40% Discovery artiste (related) FAIT
        # 100 % use bpm/dur prediction FAIT
        # 20 % track from your most listened artist FAIT
        # 20 % track from your most listened album FAIT
        # 20% Discovery genre (genre you don't listen to)

        mixLen = session['mixLen'] 
        
        bpm = predict('bpm', mixLen)
        dur = predict('duration', mixLen)

        def createMix(p1, p2):
            newTracks = []
            sortedTracks = []

            # NEW ARTIST RELATED TO FAV
            percent = round((mixLen/100)*p1)+5
            percentReste = round((mixLen/100)*p2)+5

            sampleArtist = df['artistID'].value_counts()[:percent-5].index.tolist()
            for i in sampleArtist:
                try:
                    r = requests.get(f'https://api.deezer.com/artist/{i}/related').json()['data']
                    rand = randint(0, len(r)-1)
                    artist = r[rand]['id']
                    y = requests.get(f'https://api.deezer.com/artist/{artist}/top?limit={percent}').json()['data']
                    for w in range(0,len(y)-1):
                        newTracks.append(y[w]['id'])
                except:
                    pass

            sampleAlbum = df['albumID'].value_counts()[:percentReste-5].index.tolist()
            sampleArtistBis = df['artistID'].value_counts()[:percentReste-5].index.tolist()
            
            for p in sampleAlbum:
                try:
                    r = requests.get(f'https://api.deezer.com/album/{p}').json()
                    for u in range(len(r['tracks']['data'])-1):
                        newTracks.append(r['tracks']['data'][u]['id'])
                except:
                    pass

            for f in sampleArtistBis:
                try:
                    r = requests.get(f'https://api.deezer.com/artist/{f}/top?limit={percentReste}').json()['data']
                    for q in range(len(r)-1):
                        newTracks.append(r[q]['id'])
                except:
                    pass
            
            datasTracks = []
            datasAlbum = []
            datasArtist = []

            for z in newTracks:
                try:
                    r = requests.get(f'https://api.deezer.com/track/{z}').json()
                    
                    datasArtist.append((r['artist']['id'],r['artist']['name']))
                    datasAlbum.append((r['album']['id'], r['album']['title']))

                    bpmData = r["bpm"]
                    if bpmData == 0:
                        bpmData = None
                    duration = r["duration"]

                    try:
                        genre = requests.get(f'https://api.deezer.com/album/{r["album"]["id"]}').json()["genre_id"]
                        if genre == -1:
                            genre = None
                    except:
                        genre = None

                    datasTracks.append((r["id"], r['album']['id'],genre, r['artist']['id'], r['rank'], duration, bpmData, r['title']))
                    if (bpmData in bpm) or (duration in dur):
                        sortedTracks.append(r['id'])
                except:
                    pass

            for k in sortedTracks:
                newTracks.remove(k)
            
            # IF NOT ENOUGH SORTED TRACK FILL GAP WITH GENERATED TRACKS
            try:
                dailyMix = sample(sortedTracks,mixLen)
            except:
                length = mixLen-len(sortedTracks)
                fullLen = mixLen-length
                rand = sample(newTracks,length)
                dailyMix = sample(sortedTracks,fullLen)
                for i in range(0,length):
                    dailyMix.append(rand[i])

            datasTrackUser = []
            for h in dailyMix:
                datasTrackUser.append((session["deezerID"],h))

            DBManaging.executemany("INSERT OR REPLACE INTO Albums (id_album, name) VALUES (?,?)", datasAlbum)
            DBManaging.executemany("INSERT OR REPLACE INTO Artistes (id_artiste, name) VALUES (?,?)", datasArtist)

            return {"datasTrackUser":datasTrackUser, "datasTracks":datasTracks}
    
        if session["discovery"]:
            # DISCOVERY
            datasAlbum = []
            datasArtist = []

            dataMix = createMix(40,20)
            datasTrackUser = dataMix['datasTrackUser']
            datasTracks = dataMix['datasTracks']

            # CODE DISCOVERY GENRE AND ADD TO DATA USER AND TRACS
            allGenre = DBManaging.execute_read_query('SELECT id_genre FROM Genres')
            data = DBManaging.execute_read_query('SELECT id_genre FROM Tracks INNER JOIN TracksUser ON Tracks.track_id = TracksUser.track_id WHERE deezerID = ?', (session['deezerID'],))
            genre = []
            randGenre = []
            # GET A RANDOM GENRE ID
            for o in data:
                if o[0] != None and o[0] not in genre:
                    genre.append(o[0])
            for j in allGenre:
                if not j[0] in genre and j[0] != 0:
                    randGenre.append(j[0])
            randGenre = sample(randGenre, 1)

            try:
                newGenre = requests.get(f'https://api.deezer.com/genre/{randGenre[0]}/artists').json()["data"]
                rand = randint(0,len(newGenre)-1)
                artiste = newGenre[rand]['id']
                percent = round((mixLen/100)*20)+5
                topTrack = requests.get(f'https://api.deezer.com/artist/{artiste}/top?limit={percent}').json()["data"]
                newTrack = []
                for q in range(len(topTrack)-1):
                    newTrack.append(topTrack[q]['id'])
                newTrack = sample(newTrack,percent-5)
                for k in newTrack:

                    r = requests.get(f'https://api.deezer.com/track/{z}').json()
                    
                    datasArtist.append((r['artist']['id'],r['artist']['name']))
                    datasAlbum.append((r['album']['id'], r['album']['title']))
                    
                    bpmData = r["bpm"]

                    if bpmData == 0:
                        bpmData = None
                    duration = r["duration"]

                    datasTracks.append((r["id"], r['album']['id'],randGenre[0], r['artist']['id'], r['rank'], duration, bpmData, r['title']))
            except:
                pass
        
            DBManaging.executemany("INSERT OR REPLACE INTO Albums (id_album, name) VALUES (?,?)", datasAlbum)
            DBManaging.executemany("INSERT OR REPLACE INTO Artistes (id_artiste, name) VALUES (?,?)", datasArtist)

        else:
            # NORMAL
            dataMix = createMix(40,30)
            datasTrackUser = dataMix['datasTrackUser']
            datasTracks = dataMix['datasTracks']
           
        DBManaging.executemany("INSERT INTO Daily (deezerID, track_id) VALUES (?,?)", datasTrackUser)
        DBManaging.executemany("INSERT OR REPLACE INTO Tracks (track_id, id_album, id_genre, id_artiste, score, duration, bpm, title) VALUES (?,?,?,?,?,?,?,?)", datasTracks)

        # TIMESTAMP
        now = datetime.now()
        DBManaging.execute_query("UPDATE Users set lastMix = ? WHERE deezerID = ?", (now,session["deezerID"]))
        # create mix
 
        playlist = DBManaging.execute_read_query("SELECT playlist FROM Users WHERE deezerID = ?", (session["deezerID"],))[0][0]
        
        def addTrackToPlaylist(ids):
            for i in datasTrackUser:
                r = requests.post(f'https://api.deezer.com/playlist/{ids}/tracks', {"songs": i[1],'access_token': session["token"]})
            
        # delete last playlist
        re = requests.delete(f'https://api.deezer.com/playlist/{playlist}?access_token={session["token"]}')
        
        r = requests.post('https://api.deezer.com/user/me/playlists', {"title": 'DailyMix NSI',"public": 'public', 'access_token': session["token"]})
        play = r.json()['id']
        DBManaging.execute_query("UPDATE Users SET playlist = ? WHERE deezerID = ?", (play,session["deezerID"]))
        addTrackToPlaylist(play)
        
        return 'success'
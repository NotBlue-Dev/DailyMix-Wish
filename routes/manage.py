from flask import *
import requests
from config import *

manage = Blueprint('manage', __name__, template_folder='templates')

# # # # # # # # # 
# RETURN ALL DATA FOR MAANGE PAGE
# # # # # # # # # 

@manage.route('/manage', methods=['GET','POST'])
def managePage():
    if request.method == 'GET':
        try:
            if session['loaded'] == False:
                return redirect('/process')
        except:
            return redirect('/logout')
        session['loaded'] = False
        data = session['data']
        return render_template('manage.html', username=data['name'], numberTracks=data['total'], logoPNG=data['logoPNG'], idDaily=data['daily']['id'], trackDaily=data['daily']['title'], artistDaily=data['daily']['artist'], albumDaily=data['daily']['album'], durationDaily=data['daily']['duration'], idUser=data['tracksUser']['id'], trackUser=data['tracksUser']['title'], artistUser=data['tracksUser']['artist'], albumUser=data['tracksUser']['album'], durationUser=data['tracksUser']['duration'], genre=session['discovery'], trackidUser=data['tracksUser']['trackID'], trackidDaily=data['daily']['trackID'])
    if request.method == 'POST':
        
        r = requests.get('https://api.deezer.com/user/me', {'access_token': session["token"]}).json()

        name = r["firstname"]
        logoPNG = r["picture"]

        dataTracks = DBManaging.execute_read_query('SELECT * FROM TracksUser INNER JOIN Tracks ON TracksUser.track_id = Tracks.track_id INNER JOIN Albums ON Tracks.id_album = Albums.id_album INNER JOIN Artistes ON Tracks.id_artiste = Artistes.id_artiste WHERE deezerID = ? ', (session["deezerID"],))
        
        total = DBManaging.execute_read_query('SELECT COUNT(*) FROM TracksUser WHERE deezerID = ?', (session['deezerID'],))[0][0]

        dataDaily = DBManaging.execute_read_query('SELECT * FROM Daily INNER JOIN Tracks ON Daily.track_id = Tracks.track_id INNER JOIN Albums ON Tracks.id_album = Albums.id_album INNER JOIN Artistes ON Tracks.id_artiste = Artistes.id_artiste WHERE deezerID = ? ', (session["deezerID"],))
        
        tracksUSER = {
            "id":[],
            "title":[],
            "trackID":[],
            "artist":[],
            "album":[],
            "duration":[]
        }
        
        for i in range(0,len(dataTracks)):
            tracksUSER['id'].append(i)
            tracksUSER['title'].append(dataTracks[i][9])
            tracksUSER['artist'].append(dataTracks[i][13])
            tracksUSER['album'].append(dataTracks[i][11])
            tracksUSER['duration'].append(dataTracks[i][7])
            tracksUSER['trackID'].append(dataTracks[i][1])

        dailyDATA = {
            "id":[],
            "trackID":[],
            "title":[],
            "artist":[],
            "album":[],
            "duration":[]
        }
 
        for i in range(0,len(dataDaily)):
            dailyDATA['id'].append(i)
            dailyDATA['title'].append(dataDaily[i][9])
            dailyDATA['artist'].append(dataDaily[i][13])
            dailyDATA['album'].append(dataDaily[i][11])
            dailyDATA['duration'].append(dataDaily[i][7])
            dailyDATA['trackID'].append(dataDaily[i][1])

        session['data'] = {"name":name, "logoPNG":logoPNG, "total":total, "tracksUser":tracksUSER, "daily":dailyDATA}
        
        return {"code":"done"}


from flask import *
import requests
from config import *
import datetime;

# # # # # # # # # 
# DEEZER OAUTH
# # # # # # # # # 

deezerLogin = Blueprint('deezerLogin', __name__, template_folder='templates')

@deezerLogin.route('/deezer/login', methods=['GET'])
def deezer_login():
    code = request.args.get('code')

    url = (f'https://connect.deezer.com/oauth/access_token.php?app_id={AppID}'
           f'&secret={AppSecret}&code={code}&output=json')
    response = requests.get(url)
    
    if response.text == 'wrong code':
        return render_template("login.html",token = "Invalid")  
    response = response.json()
    token = response['access_token']

    r = requests.get('https://api.deezer.com/user/me', {'access_token': token}).json()
    DBManaging.execute_query('INSERT OR REPLACE INTO Users (name, email, deezerID, token, lastMix) VALUES (?,?,?,?,?)', (r['name'], r['email'], r['id'], token, None))
    session["deezerID"] = r['id']
    session["token"] = token
    session["loaded"] = False
    session["discovery"] = True
    session['mixLen'] = 20 
    session['data'] = None

    return redirect('/')
from flask import Blueprint, redirect, session
from flask.globals import request
from config import *
import requests

delete = Blueprint('delete', __name__, template_folder='templates')

# # # # # # # # # 
# DELETE VAL
# # # # # # # # # 

@delete.route('/delete', methods=['POST'])
def deletePage():
    tp = request.form['tab'].split(",")
    playlist = DBManaging.execute_read_query("SELECT playlist FROM Users WHERE deezerID = ?", (session["deezerID"],))[0][0]
        
    tep = []
    for i in tp:
        tep.append((i,session['deezerID']))
        requests.delete(f'https://api.deezer.com/playlist/{playlist}/tracks?songs={i}&access_token={session["token"]}')

    DBManaging.executemany('DELETE FROM Daily WHERE track_id = ? and deezerID = ?',tep)
    return 'success'
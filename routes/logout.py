from flask import Blueprint, redirect, session

logout = Blueprint('logout', __name__, template_folder='templates')

# # # # # # # # # 
# CLEAR SESSION VAL 
# # # # # # # # # 

@logout.route('/logout')
def logPage():
    session["deezerID"] = None
    session["token"] = None
    return redirect('/')
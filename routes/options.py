from flask import Blueprint, redirect, session
from flask.globals import request

# # # # # # # # # 
# SET USERS OPTIONS IN SESSION
# # # # # # # # # 


options = Blueprint('options', __name__, template_folder='templates')

@options.route('/options', methods=['POST'])
def optionsgPage():
    if request.method == 'POST':
        if request.form['genre'] == "0":
            session['discovery'] = True
        else:
            session['discovery'] = False
        return 'success'
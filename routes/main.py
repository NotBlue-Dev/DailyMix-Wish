from flask import *

main = Blueprint('main', __name__, template_folder='templates')

# # # # # # # # # 
#  home page
# # # # # # # # # 

@main.route('/', methods=['GET'])
def default():
    # TEMP THIS AUTO LOGIN YOU, NEED TO BE REPLACE WITH A BUTTON
    logged = True
    
    if not session.get("deezerID"):
        logged = False
        
    return render_template('index.html', login=logged)


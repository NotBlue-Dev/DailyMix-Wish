from flask import *
from config import *

token = Blueprint('token', __name__, template_folder='templates')

# # # # # # # # # 
# DEEZER AOUTH TOKEN REDIRECTION
# # # # # # # # # 

@token.route('/token', methods=['GET'])
def tokenPage():
    access_token = request.get_json()
    if access_token == None or len(access_token) < 50 :
            url = (f'https://connect.deezer.com/oauth/auth.php?app_id={AppID}'f'&redirect_uri={Redirection}&perms=basic_access,email,manage_library,delete_library')
            return redirect(url)
    else:
        return redirect('/')
from flask import *
from flask_session import Session

from routes.logout import logout
from routes.manage import manage
from routes.token import token
from routes.deezerLogin import deezerLogin
from routes.main import main
from routes.process import process
from routes.generate import newMix
from routes.options import options
from routes.delete import delete

app = Flask(__name__, static_url_path='/static')

app.register_blueprint(logout)
app.register_blueprint(deezerLogin)
app.register_blueprint(token)
app.register_blueprint(options)
app.register_blueprint(main)
app.register_blueprint(manage)
app.register_blueprint(process)
app.register_blueprint(newMix)
app.register_blueprint(delete)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["SESSION_PERMANENT"] = True
app.config["MAX_CONTENT_LENGTH"] = 120 * 1024 * 1024
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

if __name__ == '__main__':
    app.run()

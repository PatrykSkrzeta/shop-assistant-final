from flask import Flask, current_app
from flask_login import LoginManager
from mongoengine import connect
from flask_mail import Mail
import gridfs

app = Flask(__name__)
app.config['SECRET_KEY'] = '42343242343242342344'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

app.config['MAIL_SERVER'] = 'smtp.wp.pl'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'domo241@wp.pl'
app.config['MAIL_PASSWORD'] = 'Hny2tGMJmjerivj'
mail = Mail(app)

# Połączenie z MongoDB
connect('shopasistant', host='localhost', port=27017, alias='default')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Inicjalizacja GridFS w kontekście aplikacji
def initialize_gridfs():
    with app.app_context():
        client = connect('shopasistant', host='localhost', port=27017, alias='default')
        mongo_db = client['shopasistant']  # Pobranie obiektu bazy danych
        app.fs = gridfs.GridFS(mongo_db)

initialize_gridfs()

from models import User
from routes import *

if __name__ == '__main__':
    app.run(debug=True)

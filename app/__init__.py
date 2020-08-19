import os
from datetime import timedelta


from flask import Flask
from flask_session import Session
from flask_bootstrap import Bootstrap

app = Flask(__name__)

# app.secret_key = os.urandom(24)
# app.session_type = 'filesystem'
# app.config.update(
#     SESSION_COOKIE_SAMESITE='Lax',
# )

app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)

sess = Session()
sess.init_app(app)
Bootstrap(app)

from app import routes
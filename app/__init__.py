import os
from flask import Flask
from flask_bootstrap import Bootstrap

app = Flask(__name__)

app.secret_key = os.urandom(24)
app.session_type = 'filesystem'
app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
)
Bootstrap(app)

from app import routes
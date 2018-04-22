# -*- coding: utf-8 -*-
__version__ = '0.1'
from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32).encode('hex')
app.config['JWT_SECRET_KEY'] = os.urandom(32).encode('hex')
jwt = JWTManager(app)
app.debug = True
toolbar = DebugToolbarExtension(app)

from controllers import *
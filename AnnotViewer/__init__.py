#!/usr/bin/env python

__author__ = "Brandon Geise"
__copyright__ = "Copyright 2016, Geisinger Health System"
__license__ = "Apache 2.0"

from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.sqlalchemy import SQLAlchemy
import urllib
import datetime

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py', silent=True)

#app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=5)
db = SQLAlchemy(app)

import AnnotViewer.views
import AnnotViewer.admin

 
db.create_all()
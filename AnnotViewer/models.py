#!/usr/bin/env python

__author__ = "Brandon Geise"
__copyright__ = "Copyright 2016, Geisinger Health System"
__license__ = "Apache 2.0"

from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired
from AnnotViewer import app, db
 
 
 
class User(db.Model):
    __tablename__ = app.config["TABLE_NAME"]

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    activeYN = db.Column(db.Boolean, default = False)
    user_role = db.Column(db.String, default = "User")
    tables = db.relationship('Tables',backref='userID',lazy='dynamic')
 
    def is_authenticated(self):
        return True
 
    def is_active(self):
        return self.activeYN
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.id)
    
    def is_admin(self):
        return self.user_role
    
    def __repr__(self):
        return self.username
    


class Tables(db.Model):
    __tablename__ = 'users_tables'

    id = db.Column(db.Integer, primary_key=True)
    databaseName = db.Column(db.String(50))
    tableName = db.Column(db.String(50))
    username = db.Column(db.String(100), db.ForeignKey(app.config["TABLE_NAME"] + '.username'))
    

class AuditEntry(db.Model):
    __tablename__ = 'audit_entry'
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    action_time = db.Column(db.DateTime)
    action_type = db.Column(db.String(100))
    action_outcome = db.Column(db.String(100))
    
    def __init__(self,username, action_time, action_type, action_outcome):
        self.username = username
        self.action_time = action_time
        self.action_type = action_type
        self.action_outcome = action_outcome

 
class LoginForm(Form):
    username = TextField('Username', [InputRequired()])
    password = PasswordField('Password', [InputRequired()])
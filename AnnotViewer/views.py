#!/usr/bin/env python

__author__ = "Brandon Geise"
__copyright__ = "Copyright 2016, Geisinger Health System"
__license__ = "Apache 2.0"

import pyodbc
from datetime import datetime
from flask import render_template, Flask, redirect, url_for, request,jsonify,json, Response, Blueprint, g, flash,session
from AnnotViewer import app, db
from lxml import etree
from AnnotViewer import utils
from AnnotViewer import ldapAuth
from sys import platform as _platform
import operator
from flask.ext.login import current_user, login_user, logout_user, login_required, LoginManager, user_logged_in, user_logged_out
from datetime import timedelta, datetime
import uuid
from AnnotViewer.models import User, LoginForm, Tables, AuditEntry
import collections


auth = Blueprint('auth_blueprint', __name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = ""
 
app.register_blueprint(auth)

def auditUser(sender, user):
    entry = AuditEntry(user.username, datetime.now(), 'LOGOUT', 'SUCCESS')
    db.session.add(entry)
    db.session.commit()

user_logged_out.connect(auditUser, app)
 
@app.context_processor
def add_session_config():
    """Add current_app.permanent_session_lifetime converted to milliseconds
    to context. The config variable PERMANENT_SESSION_LIFETIME is not
    used because it could be either a timedelta object or an integer
    representing seconds.
    """
    return {
        'TIMEOUT_WARNING_MS': (
            app.config['TIMEOUT_WARNING_MS']),
        'TIMEOUT_LOGOUT_MS' : (
            app.config['TIMEOUT_LOGOUT_MS']),
        'KEEPALIVE_INTERVAL_MS' : (
            app.config['KEEPALIVE_INTERVAL_MS']),
        'SITE_NAME' : ( 
            app.config['SITE_NAME']),
    }   
    

@app.before_request
def make_session_permanent():
    session.permanent = True
    session.modified = True

    

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def get_current_user():
    g.user = current_user
    
@app.route('/')
@login_required
def index():
    user = g.user

    return render_template(
        'index.html'
        , myuser = user.username
        , is_admin = user.user_role
    )

@app.route('/login',methods=['GET','POST'])
def login():
    #if not current_user.is_authenticated():

 
    form = LoginForm(request.form)
 
    if request.method == 'POST' and form.validate():
            username = request.form.get('username')
            password = request.form.get('password')
 
            if app.debug == True:
                if username == "admin" and password == "admin":
                    user = User.query.filter_by(username=username,activeYN=True).first()
                    if user:
                        login_user(user)
                        entry = AuditEntry(username, datetime.now(), 'LOGIN', 'SUCCESS')
                        db.session.add(entry)
                        db.session.commit()
                        #flash('You have successfully logged in.', 'success')
                        return redirect(url_for('index'))
                    else:
                        flash(
                        'Invalid username or password. Please try again.',
                        'danger')
                        entry = AuditEntry(username, datetime.now(), 'LOGIN', 'INVALID USER')
                else:
                     flash(
                        'Invalid username or password. Please try again.',
                        'danger')
                     entry = AuditEntry(username, datetime.now(), 'LOGIN', 'FAILED')
                     db.session.add(entry)
                     db.session.commit()
                     return render_template('login.html', form=form)
            else:
                if ldapAuth.ldapLogin(username,password):
                    user = User.query.filter_by(username=username,activeYN=True).first()
                    if user:
                        login_user(user)
                        entry = AuditEntry(username, datetime.now(), 'LOGIN', 'SUCCESS')
                        db.session.add(entry)
                        db.session.commit()
                        return redirect(url_for('index'))
                    else:
                        flash(
                        'Invalid username or password. Please try again.',
                        'danger')
                        entry = AuditEntry(username, datetime.now(), 'LOGIN', 'INVALID USER')
                else:
                     flash(
                        'Invalid username or password. Please try again.',
                        'danger')
                     entry = AuditEntry(username, datetime.now(), 'LOGIN', 'FAILED')
                     db.session.add(entry)
                     db.session.commit()
                     return render_template('login.html', form=form)
 
            
 
    if form.errors:
            flash(form.errors, 'danger')
    #else:
    #    flash('You are already logged in.')
    #    return redirect(url_for('index')) 
    return render_template('login.html', form=form)
 
 
@app.route('/logout',methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))



@app.route('/upload',methods=['GET','POST'])
@login_required
def upload():
    if request.method == 'POST':
        names = {'cas':'http:///uima/cas.ecore', 'xmi':'http://www.omg.org/XMI','textsem':"http:///org/apache/ctakes/typesystem/type/textsem.ecore",'syntax':'http:///org/apache/ctakes/typesystem/type/syntax.ecore','refsem' : 'http:///org/apache/ctakes/typesystem/type/refsem.ecore'}
        annotationTypes = ['SignSymptomMention','AnatomicalSiteMention','ProcedureMention','DiseaseDisorderMention']
        file = request.files['files[]']

        content = file.read()
        doc = etree.fromstring(content)

        sofa = utils.getSofaString(doc,names)

        annotList = utils.getAnnotations(annotationTypes,names,doc,sofa)

        return Response(json.dumps({'sofa': sofa, 'xmiAnnotations': json.dumps(sorted(annotList, key=lambda k: k['bA']) )}),mimetype='text/plain')


@app.route('/getAllAnnotations', methods=['GET'])
@login_required
def getAllAnnotations():
    if request.method == 'GET':
        dbname = request.args['dbname']
        tblname = request.args['tblname']
        con = pyodbc.connect(app.config['DATABASE_CONNECTION'])
        mycursor = con.cursor()
        mycursor.execute("select distinct accessionNum from " + dbname + "." + tblname)
        columns = [column[0] for column in mycursor.description]
        results = []
        for row in mycursor:
            results.append(dict(zip(columns,row)))
            
        con.close()

        return json.dumps(sorted(results))



@app.route('/getAnnoationsDB',methods=['GET','POST'])
@login_required
def getAnnotations():
    if request.method == 'GET':
        #Create connection to SQL Server
        accNum =  request.args['accessionNumber']
        dbname = request.args['dbname']
        tblname = request.args['tblname']
        names = {'cas':'http:///uima/cas.ecore', 'xmi':'http://www.omg.org/XMI','textsem':"http:///org/apache/ctakes/typesystem/type/textsem.ecore",'syntax':'http:///org/apache/ctakes/typesystem/type/syntax.ecore','refsem' : 'http:///org/apache/ctakes/typesystem/type/refsem.ecore'}
        annotationTypes = ['SignSymptomMention','AnatomicalSiteMention','ProcedureMention','DiseaseDisorderMention']

        con = pyodbc.connect(app.config['DATABASE_CONNECTION'])
        mycursor = con.cursor()
        mycursor.execute("select xmi from " + dbname + "." + tblname + " where accessionNum = " + accNum)
        result = mycursor.fetchone()[0]
        if result:
            if isinstance(result, unicode):
                result = result.encode("utf-8")
            doc = etree.fromstring(result)
            sofa = utils.getSofaString(doc,names)
            annotList = utils.getAnnotations(annotationTypes,names,doc,sofa)
        
        con.close()

        return Response(json.dumps({'sofa': sofa, 'xmiAnnotations': json.dumps(sorted(annotList, key=lambda k: k['bA']) )}),mimetype='text/plain')
    
@app.route('/getUserTables', methods=['GET'])    
@login_required
def getTables():
    if request.method == 'GET':
        username = g.user.username
        userTables = Tables.query.with_entities(Tables.databaseName, Tables.tableName).filter_by(username=username).all()
        result = collections.defaultdict(list)
        
        for row in userTables:
            result[row[0]].append(row[1])
    
    return jsonify(result)


@app.route("/ping", methods=['POST'])
def ping():
    session.modified = True
    return 'OK'
#!/usr/bin/env python3

from re import L
from flask import Flask, render_template, request, redirect, url_for, make_response, flash
from dotenv import dotenv_values

import pymongo
import datetime
from bson.objectid import ObjectId
import sys

# modules for user authentication
import flask_login
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

# instantiate the app
app = Flask(__name__)

#set up flask-login for user authentication
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# load credentials and configuration options from .env file
# if you do not yet have a file named .env, make one based on the template in env.example
config = dotenv_values(".env")

# turn on debugging if in development mode
if config['FLASK_ENV'] == 'development':
    # turn on debugging, if in development
    app.debug = True # debug mnode


# connect to the database
cxn = pymongo.MongoClient(config['MONGO_URI'], serverSelectionTimeoutMS=5000)
try:
    # verify the connection works by pinging the database
    cxn.admin.command('ping') # The ping command is cheap and does not require auth.
    db = cxn[config['MONGO_DBNAME']] # store a reference to the database
    print(' *', 'Connected to MongoDB!') # if we get here, the connection worked!
except Exception as e:
    # the ping command failed, so the connection is not available.
    # render_template('error.html', error=e) # render the edit template
    print(' *', "Failed to connect to MongoDB at", config['MONGO_URI'])
    print('Database connection error:', e) # debug

# class to represent user
class User(flask_login.UserMixin):
    def __init__(self,data):
        self.id = data['_id'] # shortcut to _id field
        self.data = data # all user data

def locate_user(user_id=None, email=None):
    '''
    Return a User object for the user with the given id or email address, or None if no such user exists.
    @param user_id: the user_id of the user to locate
    @param email: the email address of the user to locate
    '''
    if user_id:
        criteria = {"_id":ObjectId(user_id)}
    else:
        criteria = {"email":email}
    
    doc = db.users.find_one(criteria) # find user w/ this email
    # if user exists, create user object and return
    if doc:
        user = User(doc)
        return user
    #else
    return None

def user_loader(user_id):
    #   This function is called automatically by flask-login with every request the browser makes to the server.
    return locate_user(user_id=user_id)

# make the currently-logged-in user, if any, available to all templates as 'user'
@app.context_processor
def inject_user():
    return dict(user=flask_login.current_use)

userId = "6351acad640dc9083d534403"

# set up the routes
@app.route('/deadline') # show deadlines
def show_deadline():
    today = datetime.datetime.today() - datetime.timedelta(days = 1)
    docs = db.deadline.find({"user": ObjectId(userId), "due":{"$gte":today}}).sort("due", 1) # sort in descending order of created_at timestamp
    deadline = list(docs)
    for i in deadline:
        i["countdown"] = i["due"] - today
        i["countdown"] = i["countdown"].days
    return render_template('deadline.html', docs=deadline) 

@app.route('/deadline/add') # add deadlines
def add_deadline():
    today = str(datetime.datetime.today())
    today= today[:10]+"T"+today[11:16]
    return render_template('add_deadline.html', today=today) # render the hone template

@app.route('/deadline/add', methods=['POST'])# add deadlines confirm with post request
def submit_deadline():
    title = request.form['dtitle']
    due = request.form['dtime'].replace('T', '-').replace(':', '-').split('-')
    due = [int(v) for v in due]
    priority = request.form['dPriority']
    doc = {
        "title": title, 
        "due": datetime.datetime(*due),
        "priority": priority,
        "user": ObjectId(userId)
    }
    db.deadline.insert_one(doc)
    return redirect(url_for('show_deadline'))

@app.route('/deadline/edit') # edit deadlines page
def edit_deadline():
    today = datetime.datetime.today() - datetime.timedelta(days = 1)
    docs = db.deadline.find({"user": ObjectId(userId), "due":{"$gte":today}}).sort("due", 1) # sort in descending order of created_at timestamp
    deadline = list(docs)
    for i in deadline:
        i["countdown"] = i["due"] - today
        i["countdown"] = i["countdown"].days
    return render_template('edit_deadline.html', docs=deadline) 

@app.route('/deadline/delete/<mongoid>')
def delete_deadline(mongoid):
    db.deadline.delete_one({"_id": ObjectId(mongoid)})
    return redirect(url_for('edit_deadline')) # tell the web browser to make a request for the / route (the home function)

@app.route('/deadline/edit/<mongoid>')
def rewrite_deadline(mongoid):
    doc = db.deadline.find_one({"_id": ObjectId(mongoid)})
    time = str(doc["due"])
    time= time[:10]+"T"+time[11:16]
    today = str(datetime.datetime.today())
    today= today[:10]+"T"+today[11:16]
    return render_template('rewrite_deadline.html', doc=doc, time=time, today=today)

@app.route('/deadline/edit/<mongoid>', methods=['POST'])# add deadlines confirm with post request
def submit_edit_deadline(mongoid):
    title = request.form['dtitle']
    due = request.form['dtime'].replace('T', '-').replace(':', '-').split('-')
    due = [int(v) for v in due]
    priority = request.form['dPriority']
    doc = {
        "title": title, 
        "due": datetime.datetime(*due),
        "priority": priority,
        "user": ObjectId(userId)
    }
    db.deadline.update_one(
        {"_id": ObjectId(mongoid)}, # match criteria
        { "$set": doc }
    )
    return redirect(url_for('edit_deadline'))

# route to show account profile
@app.route('/account')
def show_account(user_id):
    author = db.users.find_one({"_id": ObjectId(user_id)})
    docs = db.posts.find({'user._id': ObjectId(user_id)})

    return render_template('account.html',author=author, docs=docs)

# route to show signup
@app.rute('/signup',methods=['GET'])
def signup():
    if flask_login.current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('home'))
    #else
    return render_template('signup.html')

# route to  handle the submission of the login form
@app.route('signup',methods=['POST'])
def signup_submit():
    email = request.form['email']
    password = request.form['password']
    hashed_password = generate_password_hash(password)

    if locate_user(email=email):
        flash('An account for {} already exists. Please log in.'.format(email))
        return redirect(url_for('login'))
    
    user_id = db.users.insert_one({"email":email, "password": hashed_password}).inserted_id
    if user_id:
        user = User({
            "_id":user_id,
            "email":email,
            "password":hashed_password
        })
        flask_login.login_user(user)
        flash('Thanks for joining, {}!'.format(user.data['email']))
        return redirect(url_for('home'))

    return 'Signup failed'

@app.route('/login',methods=['GET'])
def login():
    if flask_login.current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('You have been logged out.  Bye bye!')
    return redirect(url_for('home'))

@app.route('/login',methods=['POST'])
def login_submit():
    email = request.form['email']
    password = request.form['password']
    user = locate_user(email=email)

    if user and check_password_hash(user.data['password'],password):
        flask_login.login_user(user)
        flash('Welcome back!')
        return redirect(url_for('home'))
    return 'Login Failed :('

@app.route('/todo')
def show_todo():
    return render_template('base.html') 

# run the app
if __name__ == "__main__":
    #import logging
    #logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(debug = True)

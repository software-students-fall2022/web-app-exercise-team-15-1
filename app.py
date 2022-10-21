#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, make_response
from dotenv import dotenv_values

import pymongo
import datetime
from bson.objectid import ObjectId
import sys

# instantiate the app
app = Flask(__name__)

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


userId = "6351acad640dc9083d534403"

# set up the routes
@app.route('/deadline')
def show_deadline():
    today = datetime.datetime.today()
    docs = db.deadline.find({"user": ObjectId(userId), "due":{"$gt":today}}).sort("due", -1) # sort in descending order of created_at timestamp
    deadline = list(docs)
    for i in deadline:
        i["countdown"] = i["due"] - today
        i["countdown"] = i["countdown"].days
    return render_template('deadline.html', docs=deadline) # render the hone template

@app.route('/deadline/add')
def add_deadline():
    print(datetime.datetime.today())
    return render_template('add_deadline.html', today=datetime.datetime.today()) # render the hone template

@app.route('/deadline/add', methods=['POST'])
def submit_deadline():
    title = request.form['dtitle']
    due = request.form['dtime'].replace('T', '-').replace(':', '-').split('-')
    due = [int(v) for v in due];
    priority = request.form['dPriority']
    doc = {
        "title": title, 
        "due": datetime.datetime(*due),
        "priority": priority,
        "user": ObjectId(userId)
    }
    db.deadline.insert_one(doc)
    return redirect(url_for('show_deadline'))

@app.route('/account')
def show_account():
    return render_template('todo.html') 

@app.route('/todo')
def show_todo():
    return render_template('account.html') 
# run the app
if __name__ == "__main__":
    #import logging
    #logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(debug = True)

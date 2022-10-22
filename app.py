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

@app.route('/account')
def show_account():
    return render_template('base.html') 

#TO-DO Functions
@app.route('/todo') #show to-do list
def show_todo():
    docs = db.todo.find({"user": ObjectId(userId)})
    todo = list(docs)
    return render_template('todo.html', docs = todo)
    
@app.route('/todo/complete/<mongoid>') #set checked tasks to completed in database
def complete_task(mongoid):
    doc = db.todo.find_one({"_id": ObjectId(mongoid)})
    status = not doc["completed"]
    db.todo.update({"_id": ObjectId(mongoid)},{"$set": {"completed": status}})
    return redirect(url_for('show_todo'))

@app.route('/todo/edit') #edit to-do list
def edit_task():
    docs = db.todo.find({"user": ObjectId(userId)})
    todo = list(docs)
    date = "today"
    return render_template('edit_task.html', docs = todo)

@app.route('/todo/delete/<mongoid>')
def delete_task(mongoid):
    db.todo.delete_one({"_id": ObjectId(mongoid)})
    return redirect(url_for('edit_task'))

@app.route('/todo/edit/<mongoid>')    
def rewrite_task(mongoid):
    date = "today"
    return render_template('edit_task.html', date = date)


@app.route('/todo/add') # add deadlines
def add_task():
    date = "today"
    return render_template('add_task.html', date = date)

# run the app
if __name__ == "__main__":
    #import logging
    #logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(debug = True)

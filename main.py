"""`main` is the top level module for your Flask application."""
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
# Import the Flask Framework
from flask import Flask, make_response, Response
from flask import render_template, request, redirect, url_for, jsonify, g
import copy, datetime
import os, io, traceback, logging
from levenshtein_distance import levenshtein, iterative_levenshtein
import json
from zipfile import ZipFile
import csv
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
null = None

class Comment(ndb.Model):
    email = ndb.StringProperty()
    comment = ndb.TextProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)
    log = ndb.TextProperty(default=[])

class MobileData(ndb.Model):
    ip = ndb.StringProperty()
    data = ndb.JsonProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)


@app.route('/', methods=['POST','GET'])
def home():
    """Return a friendly HTTP greeting."""
    user = users.get_current_user()
    if user:
        logout_url = users.create_logout_url('/')
    else:
        login_url = users.create_login_url('/')
        return redirect(login_url)

    if request.method == 'GET':
        return render_template("comment.html")

    if request.method == 'POST':
        message = {"message": "successfully submitted", "status":"success"}
        user_comment = ""
        try:

            user_comment = request.form['comment']
            comment = Comment()
            comment.email = user.email()
            comment.comment = user_comment
            comment.log = request.form['log']
            comment.put()
            return render_template("comment.html", message=message)
        except Exception as e:
            traceback.print_exc()
            logging.exception("comment uploading failed")
            message['status'] = "error"
            message['message'] = "comment uploading failed"
            return render_template("comment.html", message=message)


@app.route('/mobiledata', methods=['POST'])
def mobile_data():
    try:
        ip = None
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ip = request.environ['REMOTE_ADDR']
        else:
            ip = request.environ['HTTP_X_FORWARDED_FOR']
        logging.info("data %s"%request.mimetype)
        logging.info("data %s"%request.json)
        logging.info("data %s"%request.get_data())
        logging.info("data %s"%request.get_json())
        mdata = MobileData()
        mdata.ip = ip
        mdata.data = request.get_json()
        mdata.put()
        return jsonify({"status": "success", "message": "data uploaded successfully"})
    except Exception as e:
        traceback.print_exc()
        # logging.info(dir(request))
        logging.exception("data uploading failed")
        return jsonify({"status": "error", "message": "data uploading failed"})
        
@app.route('/get_mobiledata', methods=['GET'])
def get_mobile_data():
    try:
        mobiledata = MobileData().query().fetch()
        data = []
        for entry in mobiledata:
            data.append(
                    {
                        "data": entry.data,
                        "ip": entry.ip,
                        "timestamp": entry.timestamp
                    }
                )
        print(data)
        return jsonify(records=data)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": "Exception occurred while fectching the data"})

"""
action, keystroke, epoc, levenshtein_distance
"""
@app.route('/download', methods=['GET'])
@app.route('/download', methods=['POST'])
def download():
    if request.method == 'GET':
        comment_ids = Comment().query(projection=[Comment.email], distinct=True).fetch()
        users = {}
        for comment in comment_ids:
            users[comment.email] = comment.key
        return render_template("analysis_csv.html", users=users)
    if request.method == 'POST':
        actual_text = """The Arthur C. Clarke Award is a British award given for the best science fiction novel first published in the United Kingdom during the previous year. It is named after British author Arthur C. Clarke (picture), who gave a grant to establish the award in 1987. Any "full-length" science fiction novel written or translated into English is eligible for the prize, provided that it was first publish in the United Kingdom during the prior calendar year. There is no restriction on the nationality of the author, and the publication history of works outside the United Kingdom is not taken into consideration."""
        # Got maximum recursive depth exceed error for recursive levenshtein distance methos
        # print(levenshtein(actual_text, comment[0].comment))
        # So using iterative levenshtein menthod to calculate distance
        # print(iterative_levenshtein(actual_text, comment[0].comment))
        output = {}
        # print(comment.key, comment.email)
        key = ndb.Key(urlsafe=request.form['key'])
        print("found key ", key),
        comment = key.get()
        # print(comment.email, comment.timestamp, comment.comment)
        output["email"] = comment.email
        print(output["email"])
        output["data"] = []
        for entry in json.loads(comment.log):
            output["data"].append({"action": entry['action'], "keystroke": entry['char'], "epoc": entry['timestamp'], "levenshtein_distance":iterative_levenshtein(entry['current_text'], actual_text)})
        return jsonify(output)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

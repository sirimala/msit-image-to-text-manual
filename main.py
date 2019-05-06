"""`main` is the top level module for your Flask application."""
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
# Import the Flask Framework
from flask import Flask, make_response, Response
from flask import render_template, request, redirect, url_for, jsonify, g
import copy, datetime
import os, io, traceback, logging
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
null = None

class Comment(ndb.Model):
    email = ndb.StringProperty()
    comment = ndb.TextProperty()
    timestamp = ndb.DateTimeProperty(auto_now_add=True)

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
            comment.put()
            return render_template("comment.html", message=message)
        except Exception as e:
            traceback.print_exc()
            logging.exception("comment uploading failed")
            message['status'] = "error"
            message['message'] = "comment uploading failed"
            return render_template("comment.html", message=message, user_comment=user_comment.strip())


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
        # traceback.print_exc()
        logging.info(dir(request))
        logging.exception("data uploading failed")
        return jsonify({"status": "error", "message": "data uploading failed"})
        


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

"""`main` is the top level module for your Flask application."""
from google.appengine.api import users
from google.appengine.api import mail
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
# Import the Flask Framework
from flask import Flask, make_response, Response
from flask import render_template, request, redirect, url_for, jsonify, g
import copy, datetime
import os, io, traceback
app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
null = None

@app.route('/', methods=['POST','GET'])
def home():
    """Return a friendly HTTP greeting."""
    if request.method == 'GET':
        return render_template("comment.html", **context)

    if request.method == 'POST':
        return redirect("/")

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500

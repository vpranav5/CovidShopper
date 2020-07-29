import json
import time
import usaddress
import requests
import sys
import os
from flask import Flask, session, render_template, request, url_for, session, redirect, jsonify,  send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import text
from models import ShoppingCart, db, app
from flask_cors import CORS

CORS(app)

@app.route("/")
def serve():
    """serves React App"""
    #return send_from_directory(app.static_folder, "index.html")
    #return render_template("index.html", value = "Test value")

    return render_template('index.html')
    #return render_template("Shopping.jsx")
    #return "Hello, World"

if __name__ == "__main__":
    app.debug = True
    os.system('npm install; npm run build; cd ..')
    app.run()

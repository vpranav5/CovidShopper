from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import psycopg2

app = Flask(__name__, static_folder='build', static_url_path='/')
#app = Flask(__name__)

#app = Flask(__name__, static_folder='react_ver/build', static_url_path='/')

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:shopping123@35.223.147.82/shoppingcartdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class ShoppingCart(db.Model):
    """
    Model of a Shopping Cart object
    """
    __tablename__ = 'drugstore'
 
    items = db.Column(db.String, primary_key = True, nullable=False) # name of item is unique ID
    itemQuantity = db.Column(db.Integer, nullable=False)
    itemPrice = db.Column(db.Float, nullable=False)


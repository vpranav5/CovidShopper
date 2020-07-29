from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import psycopg2

#app = Flask(__name__, static_folder='react-ver/build', static_url_path='/')
app = Flask(__name__)

#app = Flask(__name__, static_folder='react_ver/build', static_url_path='/')

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:shopping123@35.223.147.82/shoppingcartdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)


class ShoppingCart(db.Model):
    """
    Model of a Shopping Cart object
    """
    __tablename__ = 'drugstore'
    #id = db.Column(db.String, primary_key=True, nullable=False)
    items = db.Column(db.String, primary_key = True, nullable=False)
    #items = db.Column(db.String, nullable=False)
    
    

#     address = db.Column(db.String, nullable=False)
#     zipcode = db.Column(db.String, nullable=False)
#     latitude = db.Column(db.Float, nullable=False)
#     longitude = db.Column(db.Float, nullable=False)

#     opening_hours = db.Column(db.String, nullable=False)
#     business_status = db.Column(db.String, nullable=False)

#     # rating = db.Column(db.Float, nullable=False)

#     # website = db.Column(db.String, nullable=False)
#     google_maps_url = db.Column(db.String, nullable=False)
#     # phone_number = db.Column(db.String, nullable=False)
#     # img_url = db.Column(db.String, nullable=False)

#     city_id = db.Column(db.Integer, db.ForeignKey('city.id'))


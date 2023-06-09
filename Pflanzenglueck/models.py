# models.py

from .__init__ import db
from flask_login import UserMixin
    
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(1000), unique=True)
    password = db.Column(db.String(100))
    api_key = db.Column(db.String(20))


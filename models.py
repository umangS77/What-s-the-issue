from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cas import CAS
from flask_cas import login
from flask_cas import logout
from flask_cas import login_required
import os
from pprint import pprint
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///book.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['CAS_SERVER'] = 'https://login.iiit.ac.in'
app.config['CAS_AFTER_LOGIN'] = '/'
cas = CAS(app, '/cas')

class ISSUES(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	description = db.Column(db.String(200), nullable=False)
	state = db.Column(db.String(100), nullable=False)
	tags = db.Column(db.String(200), nullable=False)
	assignees = db.Column(db.String(200), nullable=True)
	owner = db.Column(db.String(100), nullable=False)
	gitlink = db.Column(db.String(100), nullable=False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<Issue %r>' % self.id

class USERS(db.Model):
	 id = db.Column(db.Integer, primary_key=True)
	 username = cas.username
	 Name = cas.Name
	 Role = db.Column(db.String(50), nullable=False)

	 def __repr__(self):
		 return '<User %r>' % self.id
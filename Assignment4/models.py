#Jordan Carr
#Models for Assignment 4

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Keep track of categories
class Cat(db.Model):
	cat_id = db.Column(db.Integer, primary_key = True)
	max = db.Column(db.Float)
	purchases = db.relationship('Purch', backref = 'cat', lazy = 'dynamic')
	name = db.Column(db.String(1000), nullable = False)
	
	def __init__(self, name, max):
		self.name = name
		self.max = max
	
#Keep track of purchases
#Must update later to keep track of dates
class Purch(db.Model):
	purch_id = db.Column(db.Integer, primary_key = True)
	cat_id = db.Column(db.Integer, db.ForeignKey('cat.cat_id'))
	name = db.Column(db.String(1000), nullable = False)
	amount = db.Column(db.Float)
	date = db.Column(db.Date)
	
	def __init__(self, name, amount, date):
		self.name = name
		self.amount = amount
		self.date = date
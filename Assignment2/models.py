from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Customer model
class Customer(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), nullable=False)
	pw = db.Column(db.String(80), nullable=False)
	events = db.relationship('Event', backref='customer', lazy='dynamic')

	def __init__(self, name, password):
		self.username = name
		self.pw = password

#Staff model
class Staff(db.Model):
	staff_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), nullable=False)
	pw = db.Column(db.String(80), nullable=False)
	events = db.relationship('Event', secondary ='event_list', backref=db.backref('staff', lazy='dynamic'), lazy='dynamic')

	def __init__(self, name, password):
		self.username = name
		self.pw = password

#Event model
class Event(db.Model):
	event_id = db.Column(db.Integer, primary_key=True)
	customer_id = db.Column(db.Integer, db.ForeignKey('customer.user_id'), nullable=False)
	date = db.Column(db.String(100), nullable=False)
	descript = db.Column(db.String(1000), nullable=False)
	event_title = db.Column(db.String(100), nullable=False)
	num_staff = db.Column(db.Integer)
	
	def __init__(self, date, description, title, customer):
		self.date = date
		self.descript = description
		self.event_title = title
		self.customer_id = customer
		self.num_staff = 0
		
	def __repr__(self):
		return "Customer: {}".format(self.customer_id) + "Event: {}".format(self.event_title) + "Description: {}".format(self.descript) + "Date: {}".format(self.date)
	
	#Help keeps track of how many staff members are running an event
	def add_staff(self):
		self.num_staff = self.num_staff + 1
		
#Event table to keep track of relations between events and staff members
event_list = db.Table('event_list', db.Column('event_id', db.Integer, db.ForeignKey('event.event_id')), db.Column('staff_id', db.Integer, db.ForeignKey('staff.staff_id')))

#Owner model
class Owner(db.Model):
	owner_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), nullable = False)
	pw = db.Column(db.String(80), nullable= False)
	
	def __init__(self):
		self.username = "owner"
		self.pw = "pass"

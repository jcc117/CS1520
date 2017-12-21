import time
import os
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash

from models import db, Staff, Owner, Customer, Event

#Create the application
app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'catering.db')

app.config.from_object(__name__)
app.config.from_envvar('CATERING_SETTINGS', silent=True)
app.debug = True

db.init_app(app)

def get_user_id(username):
	#Get the user id from the database/check if its there
	rv = Customer.query.filter_by(username=username).first()
	return rv.user_id if rv else None
	
def get_staff_id(username):
	#Get the staff id fro the database/check if its there
	rv = Staff.query.filter_by(username=username).first()
	return rv.staff_id if rv else None

#Reinitialize the database
@app.cli.command('initdb')
def initdb_command():
	db.drop_all()
	db.create_all()
	owner = Owner()
	db.session.add(owner)
	db.session.commit()
	print('Initialized the database.')
	
@app.before_request
def before_request():
	#Check if the user is in session
	g.user = None
	if 'user_id' in session:
		g.user = Customer.query.filter_by(user_id=session['user_id']).first()
	g.staff = None
	if 'staff_id' in session:
		g.staff = Staff.query.filter_by(staff_id=session['staff_id']).first()
	g.owner = None
	if 'owner_id' in session:
		g.owner = Owner.query.filter_by(owner_id=session['owner_id']).first()

@app.route('/')
def default():
	#Redirect the root page to the login page
	return redirect(url_for('login'))

#Modify so it displays error messages	
@app.route('/login/', methods=['GET', 'POST'])
def login():
	#If already logged in, redirect them to their user page
	if g.user:
		return redirect(url_for('user_page', username = g.user.username))
	if g.staff:
		return redirect(url_for('staff_page', username = g.staff.username))
	if g.owner:
		return redirect(url_for('owner'))
	#Logs the user in
	error = None
	if request.method == 'POST':
		#Check if the username is in the database
		user = Customer.query.filter_by(username=request.form['user']).first()
		if user is None:
			error = 'Invalid username'
		#Check for anyone else
		else:
			#Check for the correct password
			if user.pw == request.form['pass']:
				flash('You are logged in')
				session['user_id'] = user.user_id
				return redirect(url_for('user_page', username = user.username))
			else:
				error = 'Invalid password'
	return render_template('login.html', error=error)

#Log out the user
@app.route('/logout/')
def logout():
	#Logout the user
	if g.user:
		flash('You were logged out')
		session.pop('user_id', None)
		return render_template('logout.html')
	if g.staff:
		flash('You were logged out')
		session.pop('staff_id', None)
		return render_template('logout.html')
	if g.owner:
		flash('Owner is logged out')
		session.pop('owner_id', None)
		return render_template('logout.html')
	#If no one is in session, redirect them to the log in page
	else:
		redirect(url_for('login'))

#Display the owner's user page	
@app.route('/owner/')
def owner():
	if g.owner:
		#Check if the user is in session
		if g.owner.username == 'owner':
			event_list = Event.query.all()
			return render_template('owner.html', events= event_list)
		#Throw an error for unathorized users
		else:
			abort(401)
	elif g.staff:
		abort(401)
	elif g.user:
		abort(401)
	#If no one is in session, redirect them to the login page
	else:
		redirect(url_for('login'))

#Add a staff member
@app.route('/add_staff/', methods = ['GET', 'POST'])
def add_staff():
	#Check if the owner is logged in
	if g.owner:
		error = None
		if request.method == 'POST':
			if g.owner.username == 'owner':
				#Check for a username
				if not request.form['user']:
					error = "Username required"
				#Check for a password
				elif not request.form['pass']:
					error = "Password required"
				#Check for matching passwords
				elif request.form['pass'] != request.form['pass2']:
					error = "Passwords do not match"
				#Check if that staff username has already been taken
				elif get_staff_id(request.form['user']) is not None:
					error = "The username is already taken"
				#Add the new staff member
				else:
					db.session.add(Staff(request.form['user'], request.form['pass']))
					db.session.commit()
					return redirect(url_for('owner'))
				return render_template('add_staff.html', error=error)
			else:
				abort(401)
		else:
			#Check if the user is logged in
			if g.owner.username == 'owner':
				return render_template('add_staff.html', error=error)
			else:
				#Teehee
				abort(418)
	else:
		abort(401)

#Display the sign up page		
@app.route('/sign_up/', methods=['GET', 'POST'])
def sign_up():
	#If a user is logged in, redirect them to their userpage
	if g.user:
		return redirect(url_for('user_page', username=g.user.username))
	if g.staff:
		return redirect(url_for('staff_page', username=g.staff.username))
		abort(418)
	if g.owner:
		return redirect(url_for('owner'))
	error = None
	if request.method == 'POST':
		#Check for a username
		if not request.form['user']:
			error = 'Please enter a username'
		#Check for a password
		elif not request.form['pass']:
			error = 'Please enter a password'
		#Check for matching passwords
		elif request.form['pass'] != request.form['pass2']:
			error = 'Passwords do not match'
		#Make sure that username is not taken
		elif get_user_id(request.form['user']) is not None:
			error = 'The username is already taken'
		#Add the user to the data base
		else:
			db.session.add(Customer(request.form['user'], request.form['pass']))
			db.session.commit()
			flash('You were successfully signed up and can now log in')
			return redirect(url_for('login'))
	return render_template('sign_up.html', error=error)

#Display the user page for a customer
@app.route('/<username>', methods=['GET', 'POST'])
def user_page(username):
	if g.user:
		error = None
		#Submitting an event request
		if request.method == 'POST':
			#Make sure all fields are filled out
			if not request.form['title']:
				error = "Title Required"
			elif not request.form['description']:
				error = "Description Required"
			elif not request.form['date']:
				error = "Date Required"
			else:
				#Check for overlapping dates
				events = Event.query.all()
				flag = False
				for i in events:
					if request.form['date'] == i.date:
						flag = True
				if flag:
					error = "Sorry, we are already booked for that date."
				#Add a new event
				else:
					db.session.add(Event(request.form['date'], request.form['description'], request.form['title'], g.user.user_id))
					db.session.commit()
					flash('You added an event')
			return render_template('customer.html', events = g.user.events, error=error)
		else:
			if g.user.username == username:
				return render_template('customer.html', events = g.user.events, error=error)
			else:
				abort(401)
	elif g.staff:
		abort(401)
	elif g.owner:
		abort(401)
	else:
		return redirect(url_for('login'))

#Display the staff login page
@app.route('/staff_login/', methods=['GET', 'POST'])
def staff_login():
	#If already logged in, redirect the user to their page
	if g.user:
		return redirect(url_for('user_page', username = g.user.username))
	if g.staff:
		return redirect(url_for('staff_page', username=g.staff.username))
	if g.owner:
		return redirect(url_for('owner'))
	error = None
	if request.method == 'POST':
		#Check if the username is in the database
		staff = Staff.query.filter_by(username=request.form['user']).first()
		if staff is None:
			#Check if who logged in was the owner
			if request.form['user'] == 'owner':
				#Check for the correct password
				if 'pass' == request.form['pass']:
					flash('Owner is logged in')
					session['owner_id'] = Owner.query.first().owner_id
					return redirect(url_for('owner'))
				else:
					error='Invalid password'
			else:
				error = 'Invalid username'
		
		#Check for anyone else
		else:
			#Check for the correct password
			if staff.pw == request.form['pass']:
				flash('You are logged in')
				session['staff_id'] = staff.staff_id
				return redirect(url_for('staff_page', username = staff.username))
			else:
				error = 'Invalid password'
	return render_template('staff_login.html', error=error)

#Display the staff's userpage	
@app.route('/<username>/')
def staff_page(username):
	#Throw an error if not a staff member
	if g.user:
		abort(401)
	if g.owner:
		abort(401)
	if g.staff:
		if g.staff.username == username:
			#Render the page with all the staff's events and events they can sign up for
			return render_template('staff_page.html', events = g.staff.events, sign_ups = Event.query.filter(Event.num_staff < 3).filter(~g.staff.events.exists()).all())
		else:
			abort(401)
	
#Cancel an event for a user	
@app.route('/cancel/<ID>/')
def cancel_event(ID):
	if not ID:
		abort(401)
	if g.user:
		#Make sure the event exists
		event = Event.query.filter(Event.event_id == ID).first()
		if not event:
			abort(404)
		user = event.customer_id
		#Make sure the correct customer is canceling the event
		if g.user.user_id == user:
			Event.query.filter(Event.event_id == ID).delete()
			db.session.commit()
			return render_template('cancel.html')
		abort(401)
	if g.staff:
		abort(401)
	if g.owner:
		abort(401)

#Staff signup for an event	
@app.route('/sign_up/<ID>/')		
def event_sign_up(ID):
	#Make sure a staff member is logged in
	if not ID:
		abort(401)
	if g.user:
		abort(401)
	if g.owner:
		abort(401)
	if g.staff:
		#Make sure the staff member has not already signed up for this event
		event = Event.query.filter(Event.event_id == ID).first()
		if not event:
			abort(404)
		#Search for the event among what the user has already signed up for
		Staff.query.filter(Staff.staff_id == g.staff.staff_id).first().events.append(event)
		event.add_staff()
		db.session.commit()
	return redirect(url_for('staff_page', username=g.staff.username))	
	
app.secret_key = "really bad key"
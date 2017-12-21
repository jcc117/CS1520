#Jordan Carr
#Assignment 3

import os
import json
from flask import Flask, render_template, request, session, flash, g, redirect, url_for
from flask_restful import reqparse, abort, Api, Resource

from models import db, User, Message, ChatRoom

app = Flask(__name__)
api = Api(app)

app.config.update(dict(SEND_FILE_MAX_AGE_DEFAULT=0))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'chat.db')

app.config.from_object(__name__)
app.config.from_envvar('CHAT_SETTINGS', silent=True)
app.debug = True

db.init_app(app)

def get_user_id(username):
	rv = User.query.filter_by(username=username).first()
	return rv.user_id if rv else None

#Initialize the database	
@app.cli.command('initdb')
def initdb_command():
	db.drop_all()
	db.create_all()
	#db.session.commit()
	print("Initialized the database")

@app.before_request
def before_request():
	#Check if a user is in session
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter_by(user_id=session['user_id']).first()

#Route to the homepage/login page
@app.route("/", methods = ['GET', 'POST'])
def root_page():
	#Check if the user is already in session
	if g.user:
		return redirect(url_for('user_page', username = g.user.username))
	error = None
	if request.method == 'POST':
		#Check if a username was entered- extra precautions
		if request.form['name'] is None:
			error = "Please enter a username"
		else:
			#Check for valid username
			name = User.query.filter_by(username = request.form['name']).first()
			if name is None:
				error = "Invalid credentials"
			#Check for a password
			elif not request.form['pass']:
				error = "Please enter a password"
			#Check for correct password
			elif name.password == request.form['pass']:
				session['user_id'] = name.user_id
				flash("You have been logged in")
				return redirect(url_for('user_page', username = name.username))
			else:
				error = "Invalid credentials"
	
	return render_template("homepage.html", error = error)

#Route to the signup page, redirect to profile page if in session	
@app.route("/sign_up/", methods = ['GET', 'POST'])
def sign_up():
	if g.user:
		return redirect(url_for('user_page', username=g.user.username))
	error = None
	if request.method == 'POST':
		#Check for username
		if not request.form['name']:
			error = "Please enter a username"
		#Check for a password
		elif not request.form['pass']:
			error = "Please enter a password"
		#Check for a reentered password
		elif not request.form['pass2']:
			error = "Please reenter your password"
		#Check the passwords match
		elif request.form['pass'] != request.form['pass2']:
			error = "Passwords do not match"
		#Check for taken username
		elif get_user_id(request.form['name']) is None:
			db.session.add(User(request.form['name'], request.form['pass']))
			db.session.commit()
			return redirect(url_for('root_page'))
		else:
			error = "That username is already taken"
	return render_template("signup.html", error = error)

#Route to a profile page
@app.route("/<username>/", methods = ["GET", "POST"])
def user_page(username):
	if g.user:
		#Make sure this is the correct user
		if username == g.user.username:
			error = None
			#Signifies the user has left a chatroom: set their current_chat to null
			g.user.current_chat = None
			db.session.commit()
			if request.method == "POST":
				#Add a new chatroom
				chat = ChatRoom.query.filter_by(title = request.form['title']).first()
				if not request.form['title']:
					#Check that a title has been added
					error = "Please enter a title"
				elif chat is not None:
					error = "That title already exists"
				else:
					#Note: chatrooms can have the same titles, does not affect overall implementation
					newChat = ChatRoom(request.form['title'], g.user.user_id)
					db.session.add(newChat)
					g.user.chatrooms.append(newChat)
					db.session.commit()
			return render_template('user_page.html', user_chatrooms = g.user.chatrooms, chatrooms = ChatRoom.query.filter(ChatRoom.creator_id != g.user.user_id).all(), error = error)
		else:
			abort(401)
	#If no one is in session, redirect to the root page
	else:
		return redirect(url_for('root_page'))

#Route to a chatroom
@app.route("/chatrooms/<chatroom>/")
def chat_room(chatroom):
	if g.user:
		#Make sure the chatroom exists
		chatroom = ChatRoom.query.filter_by(title=chatroom).first()
		#print(g.user.current_chat)
		if not chatroom:
			abort(404)
		else:
			#If not in a chatroom, set the user's current_chat
			if not g.user.current_chat:
				id = int(chatroom.chat_id)
				g.user.current_chat = chatroom.chat_id
				db.session.commit()
				return render_template('chatroom.html', chat = chatroom)
			elif g.user.current_chat != chatroom.chat_id:
				#Display a page saying the user must leave the current chatroom before going to another
				abort(401)
			else:
				return render_template('chatroom.html', chat = chatroom)
	else:
		return redirect(url_for('root_page'))
#Log out the user
@app.route("/logout/")
def logout():
	if g.user:
		g.user.current_chat = None
		db.session.commit()
		session.pop('user_id', None)
		return render_template("logout.html")
	#If no one is in session, redirect to the root page
	else:
		return redirect(url_for('root_page'))

@app.route("/delete/<ID>")
def delete_chatroom(ID):
	if g.user:
		#Make sure the chatroom exists
		chat = ChatRoom.query.filter_by(chat_id = ID).first()
		if not chat:
			abort(404)
		else:
			#Make sure the chatroom is owned by the current user
			if g.user.user_id != chat.creator_id:
				abort(401)
			else:
				#Delete the messages from the chat room
				Message.query.filter_by(chat_id = ID).delete()
				#Delete the chatroom
				ChatRoom.query.filter_by(chat_id = ID).delete()
				db.session.commit()
				return redirect(url_for('user_page', username=g.user.username))
	else:
		abort(401)

#Get the latest messages from a chatroom
#Using a post request so I can send JSON data to the server, I know it's not restful		
@app.route("/get_messages/", methods=['POST'])
def get_messages():
	if g.user:
		#Get the most recent message id: note this unique to the page, not the user
		data = request.json
		#Very Temporary
		ID = g.user.current_chat
		if not ID:
			abort(404)
		rv = []
		messages = Message.query.filter_by(chat_id = ID).all()
		for i in range(data, len(messages)):
			string = "{}:{}".format(messages[i].user.username, messages[i].text)
			rv.append(string)
		return json.dumps(rv)
	else:
		abort(404)

#Add a message to a chatroom	
@app.route("/add_message/", methods=["POST"])
def add_message():
	if g.user:
		#Add a message to the chatroom
		ID = g.user.current_chat
		if not ID:
			abort(404)
		#Create a new message and add it to the appropriate chatroom
		msg = Message(request.form['texter'])
		chat = ChatRoom.query.filter_by(chat_id = ID).first()
		db.session.add(msg)
		chat.messages.append(msg)
		g.user.messages.append(msg)
		msg.chat_thread_id = ID
		chat.add(msg)
		db.session.commit()
		return "OK"
	else:
		abort(404)

#Get the id of the latest id added to the chat thread
@app.route("/get_latest_id/")
def get_latest_id():
	if g.user:
		if not g.user.current_chat:
			abort(404)
		else:
			ID = g.user.current_chat
			chat = ChatRoom.query.filter_by(chat_id = ID).first()
			return json.dumps(chat.high_msg_id)
	else:
		abort(404)

#Ensure the current chatroom still exists		
@app.route("/check_chat/")
def check_chat():
	if g.user:
		chat = ChatRoom.query.filter_by(chat_id = g.user.current_chat).first()
		if not chat:
			return json.dumps(0)
		else:
			return json.dumps(1)
	abort(404)
		
app.secret_key = "Even worse secret key"
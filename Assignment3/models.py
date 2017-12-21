#Jordan Carr
#Database and models for Assignment 3

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Class for keeping track of users
class User(db.Model):
	user_id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(100), nullable = False)
	password = db.Column(db.String(100), nullable = False)
	messages = db.relationship('Message', backref = 'user', lazy = 'dynamic')
	chatrooms = db.relationship('ChatRoom', backref = 'user', lazy = 'dynamic')
	current_chat = db.Column(db.Integer)
	
	def __init__(self, name, pw):
		self.username = name
		self.password = pw
		
#Class for keeping track of chatrooms
class ChatRoom(db.Model):
	__tablename__='chatroom'
	chat_id = db.Column(db.Integer, primary_key = True)
	creator_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
	title= db.Column(db.String(100), nullable = False)
	high_msg_id = db.Column(db.Integer)
	messages = db.relationship('Message', backref ='chatroom', lazy='dynamic')
	
	def __init__(self, title, creator_id):
		self.title = title
		self.creator_id = creator_id
		self.high_msg_id = 0
	
	#Add a message to the chatroom
	def add(self, message):
		self.high_msg_id = self.high_msg_id + 1
		message.chat_thread_id = self.high_msg_id

#Class for keeping track of messages
class Message(db.Model):
	msg_id = db.Column(db.Integer, primary_key = True)
	text = db.Column(db.String(1000), nullable = False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.username'))
	chat_id = db.Column(db.Integer, db.ForeignKey('chatroom.chat_id'))
	chat_thread_id = db.Column(db.Integer)
	
	def __init__(self, txt):
		self.text = txt
		
	def __repr__(self):
		return self.text
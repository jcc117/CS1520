#Jordan Carr
#Assignment 3 Models

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#Class for keeping track of users
class User(db.Model):
	user_id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(100), nullable = False)
	password = db.Column(db.String(100), nullable = False)
	messages = db.relationship('Message', backref = 'user', lazy = 'dynamic')
	chatrooms = db.relationship('ChatRoom', backref = 'user', lazy = 'dynamic')
	
	def __init__(self, name, pw):
		self.username = name
		self.password = pw
		
class ChatRoom(db.Model):
	
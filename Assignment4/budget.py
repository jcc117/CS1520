#Jordan Carr
#Assignment 5 server file

from flask import Flask, render_template, request, session, flash, g, redirect, url_for
from flask_restful import reqparse, abort, Api, Resource
import os
import json
from datetime import date, datetime

from models import Cat, Purch, db

app = Flask(__name__)
api = Api(app)

app.config.update(dict(SEND_FILE_MAX_AGE_DEFAULT=0))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(app.root_path, 'budget.db')

app.config.from_object(__name__)
app.config.from_envvar('BUDGET_SETTINGS', silent=True)
app.debug = True

db.init_app(app)

#Create a parser
parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('max', type = float)
parser.add_argument('amount', type = float)
parser.add_argument('date', type=str)
parser.add_argument('category', type=str)

@app.cli.command('initdb')
def initdb_command():
	db.drop_all()
	db.create_all()
	#db.session.commit()
	print("Initialized the database")

@app.route("/")
def home():
	return render_template("page.html")

#Handles categories	
class Category(Resource):
	#Return all categories and their maximum budgets
	def get(self):
		categories = Cat.query.all()
		rv = []
		for i in categories:
			rv.append({"name":str(i.name), "max":float(i.max)})
		return json.dumps(rv)
		
	#Post a new category
	def post(self):
		args = parser.parse_args()
		if not args['name'] or not args['max']:
			return json.dumps("Not enough arguments"), 400
		cat = Cat.query.filter_by(name = args['name']).first()
		#Category titles must not match each other
		if not cat:
			db.session.add(Cat(args['name'], float(args['max'])))
			db.session.commit()
			return json.dumps("Category posted successfully"), 201
		else:
			return json.dumps("Category already exists"), 409
		
	#Delete a specific category via title
	def delete(self):
		args = parser.parse_args()
		cat = Cat.query.filter_by(name = args['name']).first()
		#Make sure category exists
		if not cat:
			return json.dumps("Category does not exist"), 400
		else:
			Purch.query.filter_by(cat_id = cat.cat_id).delete()
			Cat.query.filter_by(name = args['name']).delete()
			db.session.commit()
			return json.dumps("Category successfully deleted"), 204

#Handles purchases from specific categories
class Purchase(Resource):
	#Return all purchases from the current month
	def get(self):
		today_date = datetime.now()
		today_month = today_date.month
		today_year = today_date.year
		purch = Purch.query.all()
		rv = []
		for i in purch:
			#Filter by current date
			if i.cat is not None:
				if today_month == i.date.month and today_year == i.date.year: 
					rv.append({"category":i.cat.name, "name":i.name, "amount":i.amount, "date":i.date.isoformat()})
			else:
				#Account for possible lack of category
				#Filter by current date
				if today_month == i.date.month and today_year == i.date.year: 
					rv.append({"category":"", "name":i.name, "amount":i.amount, "date":i.date.isoformat()})
		return json.dumps(rv), 200
		
	#Post a new purchase to a specific category
	def post(self):
		args = parser.parse_args()
		if not args['name'] or not args['amount'] or not args['date']:
			return json.dumps("Not enough arguments"), 400
		#Parse the date string and create a date object
		datestr = str(args['date']).split("-")
		#print(args['date'])
		#print(datestr)
		dateObj = date(int(datestr[0]), int(datestr[1]), int(datestr[2]))
		purch = Purch(args['name'], float(args['amount']), dateObj)
		db.session.add(purch)
		#Add it to that category
		if args['category']:
			cat = Cat.query.filter_by(name = args['category']).first()
			#Make sure the category exists
			if cat:
				cat.purchases.append(purch)
			else:
				return json.dumps("Category not found"), 404
		db.session.commit()
		return json.dumps("Purchase successfully added"), 201
		
api.add_resource(Category, '/cats/')
api.add_resource(Purchase, '/purchases/')
import flask
from flask import Flask, current_app, render_template, url_for, request, redirect, flash , session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# from models import db, ISSUES, USERS
from flask_cas import CAS
from flask_cas import login
from flask_cas import logout
from flask_cas import login_required
import os
from pprint import pprint


app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# app.config['SQLALCHEMY_BINDS'] = {'usersdb' : 'sqlite:///usersdb.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
db.init_app(app)

app.config['CAS_SERVER'] = 'https://login.iiit.ac.in'
app.config['CAS_AFTER_LOGIN'] = 'loginpage'
app.config['CAS_AFTER_LOGOUT'] = '/'
cas = CAS(app, '/cas')


class ISSUES(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	description = db.Column(db.String(200), nullable=False)
	state = db.Column(db.String(100), nullable=False)
	tags = db.Column(db.String(100), nullable=False)
	assignees = db.Column(db.String(200), nullable=True)
	owner = db.Column(db.String(100), nullable=False)
	gitlink = db.Column(db.String(100), nullable=False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	assignees = db.Column(db.String(1000), nullable = True)
	def __repr__(self):
		return '<Issue %r>' % self.id


class USERS(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100), nullable=True)
	Name = db.Column(db.String(100), nullable=True)
	role = db.Column(db.String(50), nullable=True)

	def __repr__(self):
	 return '<User %r>' % self.id

@app.route('/')
def login():
    return flask.redirect(flask.url_for('cas.login', _external=True))

@app.route('/loginpage')
def loginpage():
	session["username"] = cas.username
	session["Name"] = cas.attributes['cas:Name']
	current_owner = session["username"]
	current_name = session["Name"]
	isuser = USERS.query.filter_by(username = current_owner).first()
	if(isuser == None):
		temprole = 'VIEWER'
		if(current_owner == 'umang.srivastava@students.iiit.ac.in'):
			temprole = 'ADMIN'
		elif(current_owner == 'yash.amin@students.iiit.ac.in'):
			temprole = 'EDITOR'
		new_user = USERS(username = current_owner,
			Name=current_name,
			role=temprole)
		session["role"] = temprole
		try:
			db.session.add(new_user)
			db.session.commit()
		except:
			return 'Error is adding user'
	else:
		session["role"] = isuser.role
	return redirect('/homepage')


@app.route('/homepage', methods = ['GET','POST'])
def homepage():
	current_owner = session["username"]
	current_name = session["Name"]
	current_role = session["role"]
	issues = ISSUES.query.order_by(ISSUES.date_created).all()
	user = USERS.query.filter_by(username = current_owner).all()
	return render_template('/homepage.html',
		username = current_owner,
		Name = current_name,
		Role = current_role,
		issues = issues)


@app.route('/myissues')
def myissues():
	current_owner = session["username"]
	current_name = session["Name"]
	current_role = session["role"]
	user = USERS.query.filter_by(username = current_owner).all()
	myissues = ISSUES.query.filter_by(owner = current_owner).all()
	return render_template('/myissues.html',
		username = current_owner,
		Name = current_name,
		Role = current_role,
		myissues = myissues)


@app.route('/addissue', methods=['GET','POST'])
def addissue():
	current_owner = session["username"]
	current_name = session["Name"]
	current_role = session["role"]
	user = USERS.query.filter_by(username = current_owner).all()
	assigneeslist = USERS.query.filter((USERS.role == 'EDITOR') | (USERS.role == 'ADMIN') ).all()
	if request.method == 'POST':
		issue_title = request.form['title']
		issue_description = request.form['description']
		issue_state = request.form['state']
		# issue_tag_list = request.form.getlist('tags')
		# issue_tags=','.join(issue_tag_list)
		issue_tags=request.form['tags']
		issue_assignee_list = request.form.getlist('assignees')
		issue_assignees = ','.join(issue_assignee_list)
		issue_gitlink = request.form['gitlink']
		issue_owner = current_owner
		print(issue_assignees)
		new_issue = ISSUES(title=issue_title, 
			description=issue_description, 
			state=issue_state, 
			tags=issue_tags,
			gitlink=issue_gitlink, 
			owner = issue_owner,
			assignees = issue_assignees,
			)

		try:
			db.session.add(new_issue)
			db.session.commit()
			return redirect('/homepage')
		except:
			return 'There was a problem adding your issue'

	else:
		return render_template('/addissue.html',
		username = current_owner,
		Name = current_name,
		Role = current_role,
		list_of_assignees = assigneeslist
		)

@app.route('/update/<int:id>', methods = ['GET','POST'])
def update(id):
	current_owner = session["username"]
	current_name = session["Name"]
	current_role = session["role"]
	user = USERS.query.filter_by(username = current_owner).all()
	issue = ISSUES.query.get_or_404(id)
	assigneeslist = USERS.query.filter((USERS.role == 'EDITOR') | (USERS.role == 'ADMIN') ).all()
	if request.method == 'POST':
		issue.title = request.form['title']
		issue.description = request.form['description']
		issue.state = request.form['state']
		# issue_tag_list = request.form.getlist('tags')
		# issue_tags=','.join(issue_tag_list)
		issue_tags=request.form['tags']
		issue_assignee_list = request.form.getlist('assignees')
		issue.assignees = ' , '.join(issue_assignee_list)
		issue.gitlink = request.form['gitlink']
		issue.owner = current_owner

		try:
			db.session.commit()
			return redirect('/homepage')
		except:
			return 'There was a problem updating your issue'

	else:
		return render_template('update.html',username = current_owner,
		Name = current_name,
		Role = current_role,
		issue = issue,
		list_of_assignees = assigneeslist
		)


@app.route('/delete/<int:id>')
def delete(id):
    issue_to_delete = ISSUES.query.get_or_404(id)

    try:
        db.session.delete(issue_to_delete)
        db.session.commit()
        return redirect('/myissues')
    except:
        return 'There was a problem deleting that issue'

@app.route('/displayusers')
def displayusers():
	allusers = USERS.query.order_by(USERS.username).all()
	return render_template('displayusers.html',username = session["username"],
		Name = session["Name"],
		Role = session["role"],
		users = allusers)

@app.route('/changerole/<int:id>', methods = ['GET','POST'])
def changerole(id):
	user = USERS.query.get_or_404(id)
	if request.method == 'POST':
		user.role = request.form['role']
		try:
			db.session.commit()
			return redirect('/displayusers')
		except:
			return 'There was a problem in changing role'
	else:
		return render_template('changerole.html',username = session["username"],
		Name = session["Name"],
		Role = session["role"],
		user = user)

@app.route('/logout')
def logoutpage():
	session.pop("user",None)
	session.pop("Name",None)
	session.pop("role",None)
	return flask.redirect(flask.url_for('cas.logout', _external=True))

if __name__ == "__main__":
	app.run(debug=True)
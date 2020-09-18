from flask import Flask, current_app, render_template, url_for, request, redirect, flash
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
app.config['CAS_AFTER_LOGIN'] = '/'
cas = CAS(app, '/cas')
# with app.app_context():
#     print (current_app.name)

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
	username = 'aa'
	Name = 'aa'
	role = db.Column(db.String(50), nullable=True)

	def __repr__(self):
	 return '<User %r>' % self.id

# currentuser = cas.username

@app.route('/')
@login_required
def loginpage():
	global current_owner
	global current_name 
	current_owner = cas.username
	current_name = cas.attributes['cas:Name']
	user = USERS.query.filter_by(username = current_owner).all()
	if(user == None):
		# new_user = USERS(username = current_owner, Name=current_name, Role='VIEWER')
		# try:
		# 	db.session.add(new_user)
		# 	db.session.commit()
		# except:
		# 	return 'Error is adding user'
		pass
	return redirect('/homepage')


@app.route('/homepage', methods = ['GET','POST'])
def homepage():
	current_owner = cas.username
	current_name = cas.username
	issues = ISSUES.query.order_by(ISSUES.date_created).all()
	user = USERS.query.filter_by(username = current_owner).all()
	return render_template('/homepage.html',
		username = current_owner,
		Name = current_name,
		# role = user.role, 
		issues = issues)

@app.route('/myissues')
def myissues():
	current_owner = cas.username
	current_name = cas.username
	user = USERS.query.filter_by(username = current_owner).all()
	myissues = ISSUES.query.filter_by(owner = current_owner).all()
	# x=dir().count('current_owner')
	# if(x==0):
	# 	return redirect('/')
	return render_template('/myissues.html',username = current_owner,
		Name = current_name,
		# role = user.role,
		myissues = myissues)

@app.route('/addissue', methods=['GET','POST'])
def addissue():
	current_owner = cas.username
	current_name = cas.username
	user = USERS.query.filter_by(username = current_owner).all()
	if request.method == 'POST':
		issue_title = request.form['title']
		issue_description = request.form['description']
		issue_state = request.form['state']
		issue_tags = request.form['tags']
		issue_gitlink = request.form['gitlink']
		issue_owner = current_owner
	# issue_assignees = request.form['assignees']
		new_issue = ISSUES(title=issue_title, description=issue_description, state=issue_state, tags=issue_tags,gitlink=issue_gitlink, owner = issue_owner)

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
		# role = user.role,
		)

@app.route('/update/<int:id>', methods = ['GET','POST'])
def update(id):
	current_owner = cas.username
	current_name = cas.username
	user = USERS.query.filter_by(username = current_owner).all()
	issue = ISSUES.query.get_or_404(id)
	if request.method == 'POST':
		issue.title = request.form['title']
		issue.description = request.form['description']
		issue.state = request.form['state']
		issue.tags = request.form['tags']
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
		# role = user.role,
		issue = issue)


@app.route('/delete/<int:id>')
def delete(id):
    issue_to_delete = ISSUES.query.get_or_404(id)

    try:
        db.session.delete(issue_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that issue'
if __name__ == "__main__":
	app.run(debug=True)
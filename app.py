from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_cas import CAS
from flask_cas import login
from flask_cas import logout
from flask_cas import login_required
import os
from pprint import pprint

app = Flask(__name__)
app.secret_key = os.urandom(24)
cas = CAS(app, '/cas')

app.config['CAS_SERVER'] = 'https://login.iiit.ac.in'
app.config['CAS_AFTER_LOGIN'] = '/'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


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

# currentuser = cas.username

@app.route('/', methods=['GET','POST'])
@login_required

def route_root():
	issues = ISSUES.query.order_by(ISSUES.date_created).all()
	return render_template(
		'home.html',
		username = cas.username,
		Name = cas.attributes['cas:Name'],
		issues=issues
	)


@app.route('/addissue', methods=['GET','POST'])
def addissue():

    if request.method == 'POST':
        issue_title = request.form['title']
        issue_description = request.form['description']
        issue_state = request.form['state']
        issue_tags = request.form['tags']
        issue_gitlink = request.form['gitlink']
        issue_owner = cas.username
    # issue_assignees = request.form['assignees']
        new_issue = ISSUES(title=issue_title, description=issue_description, state=issue_state, tags=issue_tags,gitlink=issue_gitlink, owner = issue_owner)

        try:
            db.session.add(new_issue)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your issue'

    else:
        return render_template('/addissue.html',username = cas.username,
        Name = cas.attributes['cas:Name'])

if __name__ == "__main__":
    app.run(debug=True)
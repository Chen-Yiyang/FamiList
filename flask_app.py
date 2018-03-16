'''
database formats:

Family:
id, family name,
family password (not implemented)


User:
id, user name, user password, corresponding family name,
scores, voucher no. (not implemented))


Task:
status,                                                                         # assigned/ongoing, waiting to be rated, & rated/finished
name, time due, description,
difficulty level, feedback rate,

'''

from flask import Flask, redirect, render_template, request, url_for, session
from flask_sqlalchemy import SQLAlchemy

# flask & mySQL config
app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = 'any random string'                                            # for session

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="iycspfa",
    password="databasePW123",
    hostname="iycspfa.mysql.pythonanywhere-services.com",
    databasename="iycspfa$FamiList",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# db.create_all()                                                               # need to be executed once an only once!

class Task(db.Model):

    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True)
    taskStatus = db.Column(db.String(20))
    taskName = db.Column(db.String(20))
    taskTime = db.Column(db.String(20))
    taskdes = db.Column(db.String(1000))                                        # small d
    taskDiff = db.Column(db.Integer)
    taskFb = db.Column(db.Integer)
    taskUser = db.Column(db.String(20))

#db.create_all()

class Family(db.Model):

    __tablename__ = "family"

    id = db.Column(db.Integer, primary_key=True)
    famiName = db.Column(db.String(20))                                         # family name <= 20 chars
    famiPW = db.Column(db.String(20))                                           # family password <= 20 chars (not implemented)


class User(db.Model):                                                           # pw forgotten & will use a separate one later

    _tablename_ = "user"

    # for user account
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(20))
    userPW = db.Column(db.String(20))
    userFami = db.Column(db.String(20))                                         # corr. family name

    # for user details
    userScore = db.Column(db.Integer)
    userVoucher = db.Column(db.Integer)                                         #  (not implemented)


# db.create_all()

'''                                                                               # a few test cases
data = Family(famiName='FAMINAMETEST', famiPW='')
db.session.add(data)
db.session.commit()

data = User(userName='USERNAMETEST1', userPW = 'SECRET1', userFami='FAMINAMETEST1', userScore=0, userVoucher=0)
db.session.add(data)
db.session.commit()
'''



# sign in to family
@app.route("/", methods=["GET", "POST"])
def signin_family():
    if request.method == "GET":
        return render_template("fami_sign_in.html", error=False)

    _name = request.form['famiName']
#   _password = request.form['password']

    _family = Family.query.filter_by(famiName=_name).first()
    if _family is None:                                                         # family name doesn't exist
        return render_template("fami_sign_in.html", error=True)

    session['famiName'] = _name
#    return redirect(url_for('index'))                                           # single quotation mark
    return redirect(url_for('signin_user'))                                     # go to user sign in page       !!!!!!!!!! request param !!!!!!!!!!



# sign up a new family
@app.route("/famisignup", methods=["GET", "POST"])
def signup_family():
    if request.method == "GET":
        return render_template("fami_sign_up.html")

    _name = request.form['famiName']                                            # can set to unique family names
    _family = Family(famiName=_name, famiPW='')

    db.session.add(_family)
    db.session.commit()
    session['famiName'] = _name

    return redirect(url_for('signin_user'))



# sign in to user
@app.route("/usersignin", methods=["GET", "POST"])
def signin_user():
    if request.method == "GET":
        return render_template("user_sign_in.html", errorFlag=0)

    _name = request.form['userName']
    _password = request.form['password']

    _famiName = session['famiName']

    _user = User.query.filter_by(userName=_name).first()

    if _user is None or (_user.userFami != _famiName):                          # user name doesn't exist
        return render_template("user_sign_in.html", errorFlag=1)

    if _user.userPW != _password:                                               # user name or password is incorrect
        return render_template("user_sign_in.html", errorFlag=2)

    session['userName'] = _name

    return redirect(url_for("index"))                           # go to main page (sign in successfully)



# sign up a new user (to a family)
@app.route("/usersignup", methods=["GET", "POST"])
def signup_user():
    if request.method == "GET":
        return render_template("user_sign_up.html")

    _name = request.form['userName']                                            # can set to unique family names
    _password = request.form['password']
    _family = session['famiName']

    _user = User(userName=_name, userPW = _password, userFami=_family, userScore=0, userVoucher=0)

    db.session.add(_user)
    db.session.commit()

    session['userName'] = _name

    return redirect(url_for('index'))




# main page
@app.route("/main/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("main_layout.html", userName = session['userName'], tasks=Task.query.all() )

    _done = request.form["done"]

    _task = Task.query.filter_by(id=_done).first()
    _task.taskStatus = "Done"

    db.session.commit()

    return redirect(url_for('index'))





# new task
@app.route("/newtask/", methods=["GET", "POST"])
def new_task():
    if request.method == "GET":
        return render_template("new_task.html", userName = session['userName'])

    _status = "Ongoing"
    _name = request.form['taskName']
    _time = request.form['taskTime']
    _description = request.form['taskDes']
    _difficulty = request.form['taskDiff']
    _feedback = 0
    _user = session['userName']                                                 # need to change to random

    _task = Task(taskStatus=_status, taskName=_name, taskTime=_time, taskdes=_description, taskDiff=_difficulty, taskFb=_feedback, taskUser=_user)

    db.session.add(_task)
    db.session.commit()

    return redirect(url_for("index"))



# family profile
@app.route("/famiprofile/", methods=["GET", "POST"])
def family_profile():
    if request.method == "GET":
        return render_template("family_profile.html", userName = session['userName'])



# notification
@app.route("/notification/", methods=["GET", "POST"])
def notification():
    if request.method == "GET":
        return render_template("notification.html", userName = session['userName'])



# purchase (store)
@app.route("/purchase/", methods=["GET", "POST"])
def purchase():
    if request.method == "GET":
        return render_template("purchase.html", userName = session['userName'])





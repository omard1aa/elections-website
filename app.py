from flask import Flask, render_template, url_for, flash, request, redirect, session as login_session, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Elect, User, Base
from flask_httpauth import HTTPBasicAuth
from functools import wraps

import os
app = Flask(__name__)
engine = create_engine('sqlite:///my-db.db')
Base.metadata.bind = engine
auth = HTTPBasicAuth()

web_session = login_session

def login_required(f):
    @wraps(f)
    def x(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return x

@auth.verify_password
def verify_password(username, password):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    user = session.query(User).filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

@app.route('/')
def index():
    return render_template('index.htm')

@app.route('/elects')
def show_elects():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    elects = session.query(Elect).all()
    return render_template('elects.htm', elects=elects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    check = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = session.query(User).filter_by(username=username).first()
        if not user:
            flash('user not found')
            return render_template('login.htm', check=check)
        if not user.verify_password(password):
            flash('Incorrect password!')
            print("wrong password")
            return render_template('login.htm', check=check)
        if user:
            check = True
            flash('Verified user you have now more previliges')
            return redirect(url_for('private', name=user.username))
    else:
        return render_template('login.htm')


@app.route('/register', methods=["GET", "POST"])
def register():
    check=False
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if request.method == 'POST':
        check=False
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['confirmPassword']
        if username == '' or password == '':
            check=False
            flash('Sorry, invalid inputs!')
            return render_template('register.htm')
        elif session.query(User).filter_by(username=username).first():
            check=False
            flash('Sorry, existing user!')
            return render_template('register.htm', check=check)
        elif password != password_confirm:
            check=False
            flash('Passwords do not match')
            return render_template('register.htm', check=check)
        else:
            check=True
            newUser = User(username=username)
            newUser.hash_password(password)
            session.add(newUser)
            session.commit()
            flash('Congratulations! you have created your new account!\nLogin now to have more privileges')
            return render_template('user.htm', check=check)
    else:
        return render_template('register.htm')


@app.route("/profile/<string:name>", methods=['GET', 'POST'])
@auth.login_required
def private(name):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    elects = session.query(Elect).all()
    return render_template('user.htm', elects=elects)


@app.route("/add", methods=['GET', 'POST'])
@auth.login_required    
def add_elect():
    if request.method == 'POST':
        check = False
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        name = request.form['name']
        description = request.form['description']
        image_fname = request.form['image']
        elects = session.query(Elect).all()
        if session.query(Elect).filter_by(name=name).first():
            flash('Sorry, %s already exists' %(name))
            return render_template('user.htm', check=check)
        else:
            elect = Elect(name=name, description=description, image=image_fname)
            session.add(elect)
            session.commit()
            check = True
            flash('%s added to elects list.' %(name))
            return render_template('user.htm', check=check, elects=elects)
    else:
        return render_template('add_form.htm')
    return render_template('add_form.htm')

if __name__ == '__main__':
    app.secret_key = "Super_secret_key"
    host = '127.0.0.1'
    port = 5000
    app.debug = True
    app.run(host=host, port=port)
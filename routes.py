from app import app
from app import mongo
from flask import render_template, url_for, logging, flash, redirect, session, get_flashed_messages, request
from passlib.hash import sha256_crypt
from forms import *
from wtforms import ValidationError
from functools import wraps
from newsapi import NewsApiClient
import os

news_api_key = str(os.environ.get('NEWS_API_KEY'))



@app.route('/')
def home():
    session['news'] = False
    return render_template('home.html')





#Registering Routes

@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        blogs = []        
        if mongo.db.user.find_one({'email' : email}):
            flash('This email has already been registered')
            return render_template('register.html', form = form)
        mongo.db.user.insert({'name' : name, 'email' : email, 'username' : username, 'password' : password, 'blogs' : blogs})
        flash('You have successfully Registered. You can now login', 'succes')
        return redirect(url_for('login'))
    return render_template('register.html', form = form)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        email = form.email.data
        password_candidate = form.password.data

        if mongo.db.user.find_one({'email' : email}):
            data = mongo.db.user.find_one({'email' : email})
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = data['username']
                session['news'] = False
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('password incorrect')

        else:
            flash('User not found', 'error')
    return render_template('login.html', form = form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out')
    return redirect(url_for('login'))

#Decorator
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorised, Please login')
            return redirect(url_for('login'))
    return wrap








#News Routes

@app.route('/news/')
@app.route('/news')
def news1():
    return redirect('/news/corona/1')

@app.route('/news/<topic>/')
@app.route('/news/<topic>')
def news2(topic):
    return redirect('/news/'+topic+'/1')

@app.route('/news/<topic>/<page>')
@is_logged_in
def news(topic, page):
    session['news'] = True
    form = SearchForm()
    newsapi = NewsApiClient(api_key=news_api_key)
    articles = newsapi.get_everything(q = topic, page=int(page), language='en')['articles']
    articles = articles[0:18]
    return render_template('news.html', articles = articles, topic = topic, page = int(page), form = form, length = len(articles))

@app.route('/news/search', methods = ['POST'])
def search_news():
    form = SearchForm(request.form)
    topic = str(form.search.data).strip()
    if topic == '':
        return redirect(url_for('news1'))
    return redirect(url_for('news', topic = form.search.data, page = 1))

@app.route('/sources')
@is_logged_in
def sources():
    session['news'] = False
    newsapi = NewsApiClient(api_key=news_api_key)
    sources = newsapi.get_sources()['sources']
    return render_template('sources.html', sources = sources)










#Blogs Routes

@app.route('/dashboard')
@is_logged_in
def dashboard():
    session['news'] = False
    return render_template('dashboard.html')
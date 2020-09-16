from app import app
from app import mongo
from flask import render_template, url_for, logging, flash, redirect, session, get_flashed_messages, request
from passlib.hash import sha256_crypt
from forms import *
from wtforms import ValidationError
from functools import wraps
from newsapi import NewsApiClient
import os
from datetime import datetime
import uuid

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
        articles = []        
        if mongo.db.user.find_one({'email' : email}):
            flash('This email has already been registered', 'danger')
            return render_template('register.html', form = form)
        mongo.db.user.insert({'name' : name, 'email' : email, 'username' : username, 'password' : password, 'articles' : articles})
        flash('You have successfully Registered. You can now login', 'success')
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
                session['name'] = data['name']
                session['news'] = False
                flash('You are now logged in', 'success')
                return redirect(url_for('home'))
            else:
                flash('Password incorrect', 'danger')

        else:
            flash('User not found', 'danger')
    form.email.data = ''
    form.password.data = ''
    return render_template('login.html', form = form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', category='success')
    return redirect(url_for('login'))

#Decorator
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorised, Please login', category='danger')
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
    articles = sorted(articles, key = lambda i: i['publishedAt'], reverse=True)
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










#Dashboard Routes

@app.route('/dashboard')
@is_logged_in
def dashboard():
    articleForm = ArticleForm() 
    session['news'] = False
    user = session['username']
    data = mongo.db.user.find_one({'username' : user})
    articles = data['articles']
    return render_template('dashboard.html', articles = articles, articleForm = articleForm)

@app.route('/dashboard/add', methods = ['POST'])
@is_logged_in
def add_article():
    articleForm = ArticleForm(request.form)
    title = articleForm.title.data
    description = articleForm.description.data
    published = str(datetime.utcnow())
    user = session['username']
    data = mongo.db.user.find_one({'username' : user})   
    articles = data['articles']
    article = {
        'title': title, 
        'description' : description, 
        'publishedAt' : published,
        'id' : str(uuid.uuid1())
        }
    articles.append(article)
    mongo.db.user.update({'username' : user}, {'$set':{'articles':articles}})
    flash('Article added successfully', category='success')
    return redirect(url_for('dashboard'))

@app.route('/article/edit/<id>', methods = ['POST', 'GET'])
@is_logged_in
def editArticle(id):
    articleForm = ArticleForm(request.form)
    user = session['username']
    data = mongo.db.user.find_one({'username' : user})   
    articles = data['articles']
    if request.method == 'POST':
        for article in articles:
            if str(id) == str(article['id']):
                article['title'] = articleForm.title.data
                article['description'] = articleForm.description.data
                article['publishedAt'] = str(datetime.utcnow())
                break
        mongo.db.user.update({'username' : user}, {'$set':{'articles':articles}})
        return redirect(url_for('dashboard'))
    else:
        for article in articles:
            print(id)
            print(article['id'])
            if str(id) == str(article['id']):
                print('inside')
                articleForm.title.data = article['title']
                articleForm.description.data = article['description']
                break
        return render_template('edit.html', articleForm1 = articleForm, id = str(id))

@app.route('/article/delete/<id>')
@is_logged_in
def delete_article(id):
    user = session['username']
    data = mongo.db.user.find_one({'username' : user})   
    articles = data['articles']
    for article in articles:
        if str(id) == article['id']:
            articles.remove(article)
            break
    mongo.db.user.update({'username' : user}, {'$set':{'articles':articles}})
    return redirect(url_for('dashboard'))
from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb+srv://henil2:password1234@cluster0.6sbbr.mongodb.net/newsApplication?retryWrites=true&w=majority"
app.config['SECRET_KEY'] = 'SECRET_KEY'
mongo = PyMongo(app)

from routes import *

if __name__ == '__main__':
    app.run(port=4545, debug=True)
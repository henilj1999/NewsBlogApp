from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb://localhost:27017/newsApplication"
app.config['SECRET_KEY'] = 'SECRET_KEY'
mongo = PyMongo(app)

from routes import *

if __name__ == '__main__':
    app.run(port=4545, debug=True)
# coding=utf-8
from pymongo import MongoClient
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View


app = Flask(__name__)
bootstrap = Bootstrap(app)
nav = Nav(app)


@nav.navigation()
def mynavbar():
    return Navbar(
        '小窝',
        View('Home', 'index'),
        View('about me', 'about'),
    )


@app.route('/about')
def about():
    infos = {}
    client = MongoClient('localhost', 27017)
    db = client.movies
    coll = db.coll
    infos = coll.find_one({'name': '霸王别姬'})
    return render_template('about.html', infos=infos)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/hello/<name>')
def hello(name):
    return render_template('hello.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)

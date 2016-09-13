#!/usr/bin/python

# Coded by Siwei Liu
# Date 2016-09-06
# Version 1.0.0

import myapp
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def index():
    htmlstr = myapp.index(request.environ)
    return(htmlstr)

@app.route('/photos')
def photos():
    htmlstr = "<title>Photo Gallery</title>"
    htmlstr += myapp.listdir(request.environ)
    return(htmlstr)

@app.route('/visitors')
def visitors():
    htmlstr = "<title>Visited client database information</title>"
    htmlstr += myapp.visitor_db_query()
    return(htmlstr)

@app.route('/imgdisplay')
def imgdisplay():
    htmlstr = "<title>Photo Gallery</title>"
    htmlstr += myapp.imgdisplay(request.args.get('dir'), request.environ)
    return(htmlstr)

@app.route('/headers')
def headers():
    htmlstr = myapp.get_headers(request)
    return(htmlstr)

@app.route('/memo')
def memo():
    htmlstr = "<title>Online memo</title>"
    htmlstr += myapp.memoindex(request.environ)
    return(htmlstr)

@app.route('/writememo', methods=['POST'])
def writememo():
    title = request.form['title']
    text = request.form['text']
    return(myapp.memodb_write([title, text], request.environ))

@app.route('/memodb')
def memodb():
    htmlstr = "<title>Memo Database</title>"
    htmlstr += myapp.memodb_read(request.environ)
    return(htmlstr)

@app.route('/memoid')
def memoid():
    htmlstr = myapp.memodb_byID(request.args.get('id'), request.environ)
    return(htmlstr)

@app.route('/memopage')
def memopage():
    htmlstr = "<title>Memo Database</title>"
    htmlstr += myapp.memodb_read_page(request.args.get('id'), request.environ)
    return(htmlstr)

if __name__ == '__main__':
    app.run()


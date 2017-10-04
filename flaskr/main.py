"""
League of Lords' Flask app
"""

from flask import Flask, render_template, redirect, url_for, request, session, abort
from os import urandom
from database import Database
import imp
pwds = imp.load_source('pwds', '../pwds.py')

app = Flask(__name__)

@app.route('/')
def main():
    db = Database()
    """This the the homepage"""
    return render_template("home.html")

@app.route('/login', methods=['POST','GET'])
def login():
    if session.get('logged_in') == True:
        return ("Already logged in")

    if request.method == 'POST':
        db = Database()
        log_in = db.checkUser(username=request.form['username'],password=request.form['password'])
        if log_in == True:
            session['logged_in'] = True
            return('Logged in')
        else:
            return('Failed log in')

    else:
        return render_template('login.html')

@app.route('/createUser', methods=['POST','GET'])
def createUser():
    if not session.get('logged_in'):
        return ("Yo you ain't logged in")

    if request.method == 'POST':
        db = Database()
        db.addUser(username=request.form['username'],password=request.form['password'])
        return "Success"        

    else:
        return render_template('createUser.html')

@app.route('/addMatchup', methods=['POST', 'GET'])
def addMatchup():
    #if not session.get('logged_in'):
        #return("Yo dog you need to be an admin fo this")

    if request.method == 'POST':
        db = Database()
        year=int(request.form['year'])
        week=int(request.form['week'])
        team_one=request.form['team1']
        team_one_score=float(request.form['team1score'])
        team_two=request.form['team2']
        team_two_score=float(request.form['team2score']) 
        db.addMatchup(year=year,week=week,team_one=team_one,team_one_score=team_one_score,team_two=team_two,team_two_score=team_two_score)    

        return ("Success")

    else:
        return render_template('addMatchup.html')

if __name__ == '__main__':
    app.secret_key = urandom(pwds.KeySeed)
    app.run(host='0.0.0.0', port=5000, debug=True)

"""
League of Lords' Flask app
"""

from flask import Flask, render_template, redirect, url_for, request, session, abort
from os import urandom
from database import Database
from sortHistory import sortTeamHistory
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
    if not session.get('logged_in'):
        return("Yo dog you need to be an admin fo this")

    if request.method == 'POST':
        db = Database()
        year=int(request.form['year'])
        week=int(request.form['week'])
        team_one=request.form['team_one']
        team_one_score=float(request.form['team_one_score'])
        team_two=request.form['team_two']
        team_two_score=float(request.form['team_two_score']) 
        db.addMatchup(year=year,week=week,team_one=team_one,team_one_score=team_one_score,team_two=team_two,team_two_score=team_two_score)    

        return ("Success")

    else:
        return render_template('addMatchup.html')

@app.route('/showMatchups', methods=['GET'])
def showMatchups():
    db = Database()
    matchups = db.getMatchups()

    return render_template('showMatchups.html',matchups=matchups)

@app.route('/editMatchups', methods=['POST','GET'])
def editMatchups():
    if not session.get('logged_in'):
        return("Yo dog you need to be an admin fo this")
    db = Database()

    if request.method == 'POST':
        if 'submit' in request.form:
            id=request.form['id']
            year=int(request.form['year'])
            week=int(request.form['week'])
            team_one=request.form['team_one']
            team_one_score=float(request.form['team_one_score'])
            team_two=request.form['team_two']
            team_two_score=float(request.form['team_two_score']) 
            result = db.editMatchup(id=id,year=year,week=week,team_one=team_one,team_one_score=team_one_score,team_two=team_two,team_two_score=team_two_score)    
            if result == True:
                return ("Success")
            else:
                return ("Edit failed") 

        elif 'delete' in request.form:
            result = db.deleteMatchup(request.form['id'])
            if result == True:
                return ("Success")
            else:
                return ("Delete Failed")    
        else:
            return ("Bad designer responsible for this shit")
    else:
        matchups = db.getMatchups()
        return render_template('editMatchups.html',matchups=matchups)

#TODO: Figure out best way to deal w/ database sortTeamHistory also has an instance of db
@app.route('/PlayerHistory/<player>',methods=['GET'])
def displayPlayerHistory(player):
    db = Database()
    user = db.getUser(player)
    history = sortTeamHistory(player) 
    return render_template('showPlayerHistory.html',years=history,user=user)

@app.route('/PlayerHistory',methods=['GET'])
def playerHistory():
    db = Database()
    
    users = db.getUsers()
    return render_template('selectPlayerHistory.html',users=users)

def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

if __name__ == '__main__':
    app.secret_key = urandom(pwds.KeySeed)
    app.run(host='0.0.0.0', port=5000, debug=True)

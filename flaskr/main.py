"""
League of Lords' Flask app
"""

from flask import Flask, render_template, redirect, url_for, request, session, abort
from os import urandom
from database import Database
from sortHistory import sortTeamHistory, getUserHistory, getUserYearSummary
import imp
import os
pwds = imp.load_source('pwds', '../pwds.py')

app = Flask(__name__)
app.secret_key = urandom(pwds.KeySeed)

@app.route('/')
def main():
    """This the the homepage"""
    users = db.getUsers()
    years = db.getLeagueYears()
    return render_template("home.html", users=users, years=years)

@app.route('/login', methods=['POST','GET'])
def login():
    if session.get('logged_in') == True:
        return ("Already logged in")

    if request.method == 'POST':
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
        db.addUser(username=request.form['username'],password=request.form['password'])
        return "Success"        

    else:
        return render_template('createUser.html')

@app.route('/addMatchup', methods=['POST', 'GET'])
def addMatchup():
    if not session.get('logged_in'):
        return("Yo dog you need to be an admin fo this")

    if request.method == 'POST':
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
    matchups = db.getMatchups()

    return render_template('showMatchups.html',matchups=matchups)

@app.route('/editMatchups', methods=['POST','GET'])
def editMatchups():
    if not session.get('logged_in'):
        return("Yo dog you need to be an admin fo this")

    if request.method == 'POST':
        if 'submit' in request.form:
            id=request.form['id']
            year=int(request.form['year'])
            week=int(request.form['week'])
            team_one=request.form['team_one']
            team_one_score=float(request.form['team_one_score'])
            team_two=request.form['team_two']
            team_two_score=float(request.form['team_two_score']) 
            db.editMatchup(id=id,year=year,week=week,team_one=team_one,team_one_score=team_one_score,team_two=team_two,team_two_score=team_two_score)    
            return ("Edit sucessful")
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
    user = db.getUser(player)
    history = sortTeamHistory(player,db) 
    users = db.getUsers()
    return render_template('playerHistory.html',users=users,years=history,user=user)

@app.route('/YearStats/<year_sort>',methods=['GET'])
def displayYearStats(year_sort):
    users = db.getUsers()
    year_summary = [] 
    for user in users:
        user_years = sortTeamHistory(user.username,db)
        user_year_stats = [year for year in user_years if year.year==int(year_sort)]
        if user_year_stats != []:
            user_year_summary = getUserYearSummary(user_year_stats[0],user.username)
            year_summary.append(user_year_summary)
            
    years = db.getLeagueYears()
    users=db.getUsers()
    return render_template('yearHistory.html',year=year_sort, users=users, years=years, year_summary=year_summary)

@app.route('/LeagueHistory',methods=['GET'])
def leagueHistory():
    users = db.getUsers()
    league_history = []
    
    for user in users:
        if user.username != 'admin':
            user_years = sortTeamHistory(user.username,db)  #Something about this ruins users for the drop down nav bar display
            user_history = getUserHistory(user_years, user.username)
            user_history.user = user.name
            league_history.append(user_history)
    users = db.getUsers()
    years = db.getLeagueYears()
    return render_template('leagueHistory.html', league_history=league_history, users=users, years=years)

@app.context_processor
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

@app.before_first_request
def create_db():
    global db
    db = Database()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

import sqlalchemy
from sqlalchemy import Table,Column,String,Text,LargeBinary, ForeignKey, Integer, Float, or_, and_, UniqueConstraint,Boolean
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from database import Database
from sortHistory import sortTeamHistory,getUserYearSummary
import imp
pwds = imp.load_source('pwds', '../pwds.py')
#Set up the data base comm with pwds values
url_postgres = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % pwds.POSTGRES

if __name__== "__main__":
    db = Database()

    users = Table('users', db.meta,
        Column('username', String(50), unique=True, nullable=False, primary_key=True),
        Column('password', Text, nullable=False),
        Column('name', String(50)),
        Column('salt', Text, nullable=False),
        extend_existing=True)

    users = db.meta.tables['users'] 
    matchups = Table('matchups', db.meta,
        Column('id', Integer, primary_key=True),
        Column('team_one', String(50), ForeignKey("users.username"), nullable=False), 
        Column('team_one_score', Float, nullable=False),
        Column('team_two', String(50), ForeignKey('users.username'), nullable=False), 
        Column('team_two_score', Float, nullable=False),
        Column('year', Integer, nullable=False),
        Column('week', Integer, nullable=False),
        extend_existing=True)
    
    userYearStats = Table('user_year_stats', db.meta,
        Column('id', Integer, primary_key=True),
        Column('user', String(50), ForeignKey("users.username"), nullable=False),
        Column('year', Integer, nullable=False),
        Column('reg_season_wins', Integer, nullable=False),
        Column('reg_season_loses', Integer, nullable=False),
        Column('playoff_wins', Integer, nullable=False),
        Column('playoff_loses', Integer, nullable=False),
        Column('points_for', Integer, nullable=False),
        Column('points_against', Integer, nullable=False),
        Column('best_week', Integer, nullable=False),
        Column('worst_week', Integer, nullable=False),
        Column('won_title', Boolean, nullable=False),
        Column('con_wins', Integer, nullable=False),
        Column('con_loses', Integer, nullable=False),
        UniqueConstraint('user','year',name='user_year'),
        extend_existing=True) 

    db.meta.create_all(db.con)
        
    #Get all the users
    users = db.getUsers()
    #We want to update and create years for all users
    for user in users:
        years_matchups = sortTeamHistory(user.username, db)  #Get all the years and matchups for the user
        for year_matchup in years_matchups:
            year_summary = getUserYearSummary(year_matchup,user.username)
            year_exists = db.session.query(userYearStats).filter(and_(userYearStats.c.user==user.username,userYearStats.c.year==year_matchup.year)).first() 
            if year_exists != None:
                update = userYearStats.update().where(and_(userYearStats.c.user==user.username,userYearStats.c.year==year_matchup.year)).values(won_title=year_summary.winTitle,reg_season_wins=year_summary.reg_season_wins,reg_season_loses=year_summary.reg_season_loses,playoff_wins=year_summary.playoff_wins,playoff_loses=year_summary.playoff_loses,points_for=year_summary.points_for,points_against=year_summary.points_against,best_week=year_summary.best_week,worst_week=year_summary.worst_week,con_wins=year_summary.con_wins,con_loses=year_summary.con_loses)
                db.con.execute(update)
            else:
                update = userYearStats.insert().values(user=user.username,year=year_matchup.year,won_title=year_summary.winTitle,reg_season_wins=year_summary.reg_season_wins,reg_season_loses=year_summary.reg_season_loses,playoff_wins=year_summary.playoff_wins,playoff_loses=year_summary.playoff_loses,points_for=year_summary.points_for,points_against=year_summary.points_against,best_week=year_summary.best_week,worst_week=year_summary.worst_week,con_wins=year_summary.con_wins,con_loses=year_summary.con_loses)
                db.con.execute(update)
                

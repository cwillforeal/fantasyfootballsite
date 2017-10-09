import sqlalchemy
from sqlalchemy import Table,Column,String,Text,LargeBinary, ForeignKey, Integer, Float, or_
from sqlalchemy.orm import sessionmaker
import hashlib
import uuid
import imp
pwds = imp.load_source('pwds', '../pwds.py')
#Set up the data base comm with pwds values
url_postgres = 'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % pwds.POSTGRES

#Create Database comm class
#TODO: Catch if we can't talk to the database
class Database():
    def __init__(self):
        #Connect to the database, currently using default settings
        self.con = sqlalchemy.create_engine(url_postgres, client_encoding='utf8')

        #Bind the connection ot MetaData()
        self.meta = sqlalchemy.MetaData(bind=self.con, reflect=True)

        #Get a session going
        Session = sessionmaker()
        Session.configure(bind=self.con)
        self.session = Session() 

        if 'users' not in self.meta.tables:
            users = Table('users', self.meta,
                Column('username', String(50), unique=True, nullable=False, primary_key=True),
                Column('password', Text, nullable=False),
                Column('name', String(50)),
                Column('salt', Text, nullable=False))

            self.meta.create_all(self.con)

        if 'matchups' not in self.meta.tables:
            users = self.meta.tables['users'] 
            matchups = Table('matchups', self.meta,
                Column('id', Integer, primary_key=True),
                Column('team_one', String(50), ForeignKey("users.username"), nullable=False), 
                Column('team_one_score', Float, nullable=False),
                Column('team_two', String(50), ForeignKey('users.username'), nullable=False), 
                Column('team_two_score', Float, nullable=False),
                Column('year', Integer, nullable=False),
                Column('week', Integer, nullable=False))
            
            self.meta.create_all(self.con)

    def addUser(self,username,password):
        users = self.meta.tables['users']

        salt = uuid.uuid4().hex
        password_hash = hashlib.sha256(salt.encode() + password.encode()).hexdigest()
        
        #Add the new user
        add_user = users.insert().values(username=username, password=password_hash, salt=salt)
        self.con.execute(add_user)

    def checkUser(self,username,password):
        users = self.meta.tables['users']

        cur_user = self.session.query(users).filter(users.c.username == username).first()
        if cur_user == None:
            return None

        password_hash = cur_user.password
        salt = cur_user.salt 
        return password_hash == hashlib.sha256(salt.encode() + password.encode()).hexdigest()

    def getUsers(self):
        users = self.meta.tables['users']

        return self.con.execute(users.select())

    def getUser(self,user):
        users = self.meta.tables['users']

        return (self.session.query(users).filter(users.c.username == user).first())

    def addMatchup(self,year,week,team_one,team_one_score,team_two,team_two_score):
        matchups = self.meta.tables['matchups']

        add_matchup = matchups.insert().values(year=year,week=week,team_one=team_one,team_one_score=team_one_score,team_two=team_two,team_two_score=team_two_score)
        self.con.execute(add_matchup)

    def getMatchups(self):
        matchups = self.meta.tables['matchups']

        return self.con.execute(matchups.select())
    
    def deleteMatchup(self,id):
        matchups = self.meta.tables['matchups']

        delete = matchups.delete().where(matchups.c.id == id)
        self.con.execute(delete)
        
        return True

    def editMatchup(self,id,year,week,team_one,team_one_score,team_two,team_two_score):
        matchups = self.meta.tables['matchups']

        print("Here")
        edit_matchup = matchups.update().where(matchups.c.id == id).values(year=year,week=week,team_one=team_one,team_one_score=team_one_score,team_two=team_two,team_two_score=team_two_score)
        self.con.execute(edit_matchup)
    
    def getUserHistory(self,user):
        matchups = self.meta.tables['matchups']

        user_matchups = matchups.select().where(or_(matchups.c.team_one == user,matchups.c.team_two == user))
        return self.con.execute(user_matchups) 

    def getUserYears(self,user):
        matchups = self.meta.tables['matchups']

        return self.session.query(matchups.c.year).distinct().all()

    def getUserMatchupsInYear(self,user,year):
        matchups = self.meta.tables['matchups']

        matchups_year = matchups.select().where(or_(matchups.c.team_one == user,matchups.c.team_two == user)).where(matchups.c.year==year)
        return self.con.execute(matchups_year)


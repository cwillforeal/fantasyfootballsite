import sqlalchemy
from sqlalchemy import Table,Column,String,Text,LargeBinary
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
                Column('username', String(50), unique=True),
                Column('password', Text, nullable=False),
                Column('salt', Text, nullable=False))

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


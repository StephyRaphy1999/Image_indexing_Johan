from Image import app
from Image import db,app




from Image import db,app,login_manager
from flask_login import UserMixin
from flask_table import Table, Col, LinkCol
from sqlalchemy import ForeignKey
# from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(id):
    return register.query.get(int(id))

class register(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    email= db.Column(db.String(80))
    number= db.Column(db.String (10))
    password = db.Column(db.String(80))
    utype = db.Column(db.String(80))
    age = db.Column(db.String(80))
    dob = db.Column(db.String(80)) 
    image=db.Column(db.String(80))
    status=db.Column(db.String(80),default='NULL')

class complaint(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    userid= db.Column(db.Integer,ForeignKey('register.id'))
    sub = db.Column(db.String(80))
    message = db.Column(db.String(200))
    response = db.Column(db.String (200))
    status=db.Column(db.String(80),default='NULL')

class image(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    userid= db.Column(db.Integer,ForeignKey('register.id'))
    image=db.Column(db.String(80))
    title=db.Column(db.String(80))
    imgtype=db.Column(db.String(80))
    rate=db.Column(db.Integer)

class contest(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    userid= db.Column(db.Integer,ForeignKey('register.id'))
    title= db.Column(db.String(80))
    start_date= db.Column(db.String(80))
    end_date= db.Column(db.String(80))
    rules = db.Column(db.String(200))
    details= db.Column(db.String(200))
    image=db.Column(db.String(80))
    prize_1=db.Column(db.String(80))
    prize_2=db.Column(db.String(80))
    prize_3=db.Column(db.String(80))

class bookings(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    userid= db.Column(db.Integer,ForeignKey('register.id'))
    image_id= db.Column(db.Integer,ForeignKey('image.id'))
    
class contest_entry(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True) 
    userid= db.Column(db.Integer,ForeignKey('register.id'))
    contest_id= db.Column(db.Integer,ForeignKey('contest.id'))
    image=db.Column(db.String(80))
    date= db.Column(db.String(80))
    status=db.Column(db.String(80),default='NULL')


from Image import app
from Image import db,app




from Image import db,app,login_manager
from flask_login import UserMixin
from flask_table import Table, Col, LinkCol
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
   
  
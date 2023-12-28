from flask import Flask, render_template, request, redirect,  flash, abort, url_for
from Image import app,mail
from Image.models import *
from flask_login import login_user, current_user, logout_user, login_required
from random import randint
import os
from PIL import Image
from flask_session import Session
from flask import session
from flask_login import LoginManager
from flask_mail import Message

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        admin = register.query.filter_by(email=email, password=password,utype= 'admin').first()
        contributor=register.query.filter_by(email=email,password=password, utype= 'Contributor').first()
        user=register.query.filter_by(email=email,password=password, utype= 'User').first()

        if admin:
            session['uid']=admin.id
            session['ut']=admin.utype

            login_user(admin)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/') 

        elif contributor:
            session["uid"]=contributor.id
            session["ut"]=contributor.utype

            login_user(contributor)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/') 

        elif user:
            session['uid']=user.id
            session['ut']=user.utype

            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/')  
        else:
            return render_template("Login.html")
    return render_template("Login.html")

@app.route('/register',methods=['GET', 'POST'])
def registration():

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        dob=request.form['dob']
        number = request.form['number']
        email = request.form['email']
        password = request.form['password']
        utype = request.form['utype']
        
        image = request.files['image']
        pic_file = save_to_uploads(image)
        view = pic_file
        a = register.query.filter_by(email=email).first()
        if a:
            return render_template("Register.html",alert=True)
        else:

            my_data = register(name=name,age=age,dob=dob,email=email,number=number,password=password,image=view,utype=utype)
            db.session.add(my_data) 
            db.session.commit()
            return render_template("login.html",alert=True)

    return render_template("Register.html")

from flask_login import current_user, logout_user, login_required

@login_required
@app.route('/Logout')
def logout():
    print("------------1------------")
    if current_user.is_authenticated:
        print("--------------2------------------")
        user_id = current_user.id  # Assuming your User model has an 'id' attribute
        session["uid"] = user_id
        logout_user()
    return redirect('/')

@login_required
@app.route('/v_users')
def vw_users():
    a = register.query.filter_by(utype="User").all()
    return render_template("viewuser.html",a=a)

@login_required
@app.route('/v_contributor')
def vw_contributors():
    a = register.query.filter_by(utype="Contributor",status="NULL").all()
    return render_template("viewcon.html",a=a)

@login_required
@app.route('/va_contributor')
def approved_contributors():
    b = register.query.filter_by(utype="Contributor",status="approve").all()
    return render_template("viewcon.html",b=b)

@login_required
@app.route('/vr_contributor')
def rejecteed_contributors():
    c = register.query.filter_by(utype="Contributor",status="reject").all()
    return render_template("viewcon.html",c=c)


@login_required
@app.route('/approve_contributor/<int:id>')
def approve_contributor(id):
    c= register.query.get_or_404(id)
    c.status = 'approve'
    db.session.commit()
    a_sendmail(c.email)
    return redirect('/v_contributor')

def a_sendmail(email):
    msg = Message('Approved Successfully',recipients=[email])
    msg.body = f''' Congratulations , Your  Registeration is approved successfully... Now You can login using email id and password '''
    mail.send(msg)

@login_required
@app.route('/reject_contributor/<int:id>')
def reject_contributor(id):
    c= register.query.get_or_404(id)
    c.status = 'reject'
    db.session.commit()
    r_sendmail(c.email)
    return redirect('/v_contributor')

def r_sendmail(email):
    msg = Message('Registeration Rejected',recipients=[email])
    msg.body = f''' Sorry , Your  Registeration is rejected. '''
    mail.send(msg)









def save_to_uploads(form_picture):
    random_hex = random_with_N_digits(14)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = str(random_hex) + f_ext
    print(app.root_path)
    picture_path = os.path.join(app.root_path, 'static/uploads', picture_fn)
    
    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn
   

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)





















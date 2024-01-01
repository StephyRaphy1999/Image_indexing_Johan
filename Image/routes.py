from flask import Flask, render_template, request, redirect,  flash, abort, url_for
from Image import app,mail
from Image.models import *
from flask_login import login_user, current_user, logout_user, login_required
from random import randint
import os
import PIL
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
        print(name)
        age = request.form['age']
        dob=request.form['dob']
        number = request.form['number']
        email = request.form['email']
        password = request.form['password']
        utype = request.form['utype']
        
        image = request.files['image']
        print(image)
        pic_file = save_to_uploads(image)
        view = pic_file
        a = register.query.filter_by(email=email).first()
        if a:
            return render_template("Register.html")
        else:

            my_data = register(name=name,age=age,dob=dob,email=email,number=number,password=password,image=view,utype=utype)
            db.session.add(my_data) 
            db.session.commit()
            return render_template("Register.html",alert=True)

    return render_template("Register.html")

from flask_login import current_user, logout_user, login_required

@app.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        session.clear()  # Clear the session data
        print("Logout successful")
        return redirect('/')  # Redirect to the home page or another page after logout
    except Exception as e:
        print("Logout failed with error:", str(e))
        return redirect('/')




# //Admin functions//
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

@login_required
@app.route('/complaints',methods=['GET', 'POST'])
def complaints():
    uid = current_user.id
    if request.method == 'POST':
        sub = request.form['sub']
        message = request.form['message']
        my_data = complaint(sub=sub,message=message,userid=uid)
        db.session.add(my_data) 
        db.session.commit()
        return render_template("complaints.html",alert=True)

    return render_template("complaints.html")

@login_required
@app.route('/v_comp')
def vw_complaints():
    a = complaint.query.filter_by(status="NULL").all()
    return render_template("viewcomplaints.html",a=a)

@login_required
@app.route('/response/<int:id>',methods=['GET', 'POST'])
def response(id):
    c= complaint.query.get_or_404(id)
    if request.method == 'POST':
        c.response =request.form['response']
        c.status="responded"
        db.session.commit()
        return redirect('/v_comp')
    return render_template("response.html")


# //Admin functions//

#//contributor functions
@login_required
@app.route('/add_img',methods=['GET', 'POST'])
def add_image():
    if request.method == 'POST':
        # image = request.form['image']
        # pic_file = save_to_uploads(image)
        # view = pic_file

        title = request.form['title']
        imgtype= request.form['imgtype']
        rate= request.form['rate']
        my_data = image(title=title,imgtype=imgtype,rate=rate)
        db.session.add(my_data) 
        db.session.commit()
        return render_template("addimage.html",alert=True)
    return render_template("addimage.html")


#//contributor functions

def r_sendmail(email):
    msg = Message('Registeration Rejected',recipients=[email])
    msg.body = f''' Sorry , Your  Registeration is rejected.'''
    mail.send(msg)









def save_to_uploads(form_picture):
    random_hex = random_with_N_digits(14)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = str(random_hex) + f_ext
    print(app.root_path)
    picture_path = os.path.join(app.root_path, 'static/uploads', picture_fn)
    
    output_size = (500, 500)
    i = PIL.Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn
   

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)





















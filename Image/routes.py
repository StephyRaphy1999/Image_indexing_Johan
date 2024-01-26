from flask import Flask, render_template, request, redirect,  flash, abort, url_for,send_file
from Image import app,mail
from Image.models import *
from flask_login import login_user, current_user, logout_user, login_required
from random import randint
import os
import PIL
import secrets
from PIL import Image
from flask_session import Session
from flask import session
from flask_login import LoginManager
from flask_mail import Message
from datetime import datetime
from flask_login import current_user

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
        contributor=register.query.filter_by(email=email,password=password, utype= 'Contributor',status='approve').first()
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
            return render_template("Login.html",alert=True)
    return render_template("Login.html")

@app.route('/forgot',methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        a = register.query.filter_by(email=email).first()
        password_length = 4
        password=secrets.token_urlsafe(password_length)
        f_sendmail(email,password)
        a.password=password

        db.session.commit()
        return render_template("index.html",b_alert=True)
    return render_template("forgot_pass.html")


def f_sendmail(email,password):
    msg = Message('New password',recipients=[email])
    msg.body = f'Your new password is:{password}'
    mail.send(msg)

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
        print(image)
        pic_file = save_to_uploads(image)
        view = pic_file
        a = register.query.filter_by(email=email).first()
        if a:
            return render_template("Register.html",alert=True)
        else:

            my_data = register(image=view,name=name,age=age,dob=dob,email=email,number=number,password=password,utype=utype)
            db.session.add(my_data) 
            db.session.commit()
            return render_template("Register.html",acc=True)  

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
        my_data = complaint(sub=sub,message=message,user_id=uid)
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
        return render_template('viewcomplaints.html',alert=True)
    return render_template("response.html")


@login_required
@app.route('/manage_bookings')
def manage_bookings():
    a=bookings.query.all()
    return render_template("view_bookings.html",a=a)


# //Admin functions//


#//contributor functions
@login_required
@app.route('/add_img',methods=['GET', 'POST'])
def add_image():
    uid = current_user.id
    if request.method == 'POST':
        file = request.files['image']
        pic_file = save_to_uploads(file)
        view = pic_file
        print(view)

        title = request.form['title']
        imgtype= request.form['imgtype']
        rate= request.form['rate']
        my_data = image(title=title,image=view,imgtype=imgtype,rate=rate,user_id=uid)
        db.session.add(my_data) 
        db.session.commit()
        return render_template("addimage.html",alert=True)
    return render_template("addimage.html")

@login_required
@app.route('/add_contest',methods=['GET', 'POST'])
def add_con():
    uid = current_user.id
    if request.method == 'POST':
        title = request.form['title']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        rules = request.form['rules']
        details = request.form['details']
        entry_fee = request.form['rate']
        image = request.files['image']
        pic_file = save_to_uploads(image)
        view = pic_file
        prize_1 = request.form['prize_1']
        prize_2 = request.form['prize_2']
        prize_3 = request.form['prize_3']

        
        my_data = contest(user_id=uid,title=title,start_date=start_date,end_date=end_date, rules= rules,entry_fee=entry_fee,image=view,details=details,prize_1=prize_1,prize_2=prize_2,prize_3=prize_3)
        db.session.add(my_data) 
        db.session.commit()
        return render_template("contestadd.html",alert=True)
    return render_template("contestadd.html")


@login_required
@app.route('/v_image')
def v_image():
    uid = current_user.id
    a = image.query.filter_by(user_id=uid).all()
    return render_template("view_image.html",a=a)
   
@login_required
@app.route('/edit_img/<int:id>',methods=['GET', 'POST'])
def edit_image(id):
    a = image.query.filter_by(id=id).first() 
    if request.method == 'POST':
        a.title = request.form['title']
        a.imgtype = request.form['imgtype']
        a.rate = request.form['rate']
        images = request.files['image']
        pic_file = save_to_uploads(images)
        a.image = pic_file
        
        db.session.commit()
        return render_template("edit_image.html",a=a,alert=True) 
    else :
        return render_template("edit_image.html",a=a)

@login_required
@app.route('/delete_image/<int:id>')
def delete_image(id):
    delete = image.query.get_or_404(id)
    try:
        db.session.delete(delete)
        db.session.commit()
        return redirect('/v_image') 
    except:
        return 'There was a problem deleting that task'

@login_required
@app.route('/vw_contest')
def view_con():
    uid = current_user.id
    a = contest.query.filter_by(user_id=uid).all()
    return render_template("view_contest.html",a=a)

@login_required
@app.route('/edit_con/<int:id>',methods=['GET', 'POST'])
def edit_contest(id):
    a = contest.query.filter_by(id=id).first() 
    if request.method == 'POST':
        a.title = request.form['title']
        a.start_date = request.form['start_date']
        a.end_date = request.form['end_date']
        a.rules = request.form['rules']     
        a.details = request.form['details']
        a.entry_fee=request.form['rate']
        a.prize_1 = request.form['prize_1']
        a.prize_2 = request.form['prize_2']
        a.prize_3 = request.form['prize_3']

        db.session.commit()
        return render_template("edit_contest.html",a=a,alert=True) 
    else :
        return render_template("edit_contest.html",a=a)


@login_required
@app.route('/delete_contest/<int:id>')
def delete_contest(id):
    delete = contest.query.get_or_404(id)
    try:
        db.session.delete(delete)
        db.session.commit()
        return redirect('/vw_contest') 
    except:
        return 'There was a problem deleting that task'

@login_required
@app.route('/vw_profile')
def view_profile():
    a =  register.query.filter_by(id=current_user.id).first()
    return render_template("view_profile.html",a=a)


@login_required
@app.route('/vw_comp')
def view_complaints():
    uid=current_user.id
    a = complaint.query.filter_by(user_id=uid).all()
    return render_template("viewcomplaints.html",a=a)


@app.route('/view_contest_reg')
@login_required
def view_con_reg():
    user_id = current_user.id
    a = contest.query.filter_by(user_id=user_id).all()
    b = []

    for i in a:
        contest_entries = contest_entry.query.filter_by(contest_id=i.id).all()
        b.extend(contest_entries)

    return render_template("view_registrations.html", a=a, b=b)


@login_required
@app.route('/vw_bookings')
def view_bookings():
    uid=current_user.id
    a = image.query.filter_by(user_id=uid).all()
    b= []

    for i in a:
        booking_entries=bookings.query.filter_by(image_id=i.id).all()
        b.extend(booking_entries)

    return render_template("view_bookings.html",a=a,b=b)

@login_required
@app.route('/join_contest')
def vw_contest():
    u_id=current_user.id
    a = contest.query.filter(contest.user_id != u_id).all()
    return render_template("join_contributor.html",a=a)

#//contributor functions


# user functions

@login_required
@app.route('/view_contest')
def view_contest():
    a = contest.query.all()
    return render_template("view_contest.html",a=a)

@login_required
@app.route('/view_image')
def view_image():
    a = image.query.all()
    return render_template("view_image.html",a=a)


@login_required
@app.route('/payment_contest/<int:id>')
def payment(id):
    contest_id=contest.query.filter_by(id=id).first()
    c=contest_id.id
    return render_template("payment.html",c=c)


@login_required
@app.route('/reg_contest/<int:id>',methods=['GET', 'POST'])
def reg_contest(id):
    contest_id=contest.query.filter_by(id=id).first()
    uid=current_user.id
    if request.method == 'POST':
        image = request.files['image']
        pic_file = save_to_uploads(image)
        view = pic_file
        status='paid'
        date = datetime.now()
        print(date)


        my_data = contest_entry(user_id=uid,contest_id=contest_id.id,image=view,status=status,date=date)
        db.session.add(my_data)
        db.session.commit()
        return render_template('index.html',aler=True)

    return render_template("reg_contest.html")


@login_required
@app.route('/vw_contest_reg')
def view_contest_reg():
    uid = current_user.id
    a = contest_entry.query.filter_by(user_id=uid).all()
    return render_template("view_registrations.html",a=a)


@login_required
@app.route('/view_bookings')
def booking():
    uid=current_user.id
    a = bookings.query.filter_by(user_id=uid).all()
    return render_template("view_bookings.html",a=a)


@login_required
@app.route('/payment_image/<int:id>',methods=['GET', 'POST'])
def payment_1(id):
    img=image.query.filter_by(id=id).first()
    c=img.id
    uid=current_user.id
    a = register.query.filter_by(id=uid).first()
    print(a.email)
    if request.method == 'POST':      
        my_data = bookings(user_id=uid,image_id=c)
        db.session.add(my_data)
        db.session.commit()
        email=a.email
        i_sendmail(email)
        a = image.query.all()
        return render_template("view_image.html",b_alert=True,a=a)
        
    return render_template("Payments_1.html")


def i_sendmail(email):
    msg = Message('Galleria',recipients=[email])
    msg.body = f''' Sorry , Your  Registeration is rejected.'''
    mail.send(msg)



@app.route('/download/<int:id>')
def download(id):
    upload = image.query.filter_by(id=id).first()
    a = upload.image
    return  send_file("C:/Users/user/Desktop/Galleria/Image/static/uploads/"+a,as_attachment=True)
 
# user functions



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





















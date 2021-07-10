from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
import smtplib
from flask_jwt_extended import create_access_token, decode_token, JWTManager
from return_time import return_expiry_time
from db import register_user, validate_user, get_email, update_password,save_student_details,sc_requirement_update, get_colleges, collegedetails,\
    studentdetails, check_student,save_college_details,save_school_details,acheivement_save
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import os
import base64
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl



app = Flask(__name__)
app.secret_key = 'Hack@utsav'
jwt = JWTManager(app)


PEOPLE_FOLDER = os.path.join('static', 'upload')
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'pdf'])

k=''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def first():
    return render_template('welcome.html')

@app.route('/logout',  methods=['GET', 'POST'])
def logout():
    return redirect(url_for('first'))


def calculate(percent,lis):
    scor = 0
    for i,x in enumerate(lis):
        if i==0:
            scor+=x
        elif i==1:
            scor+=x*0.75
        elif i==2:
            scor+=x*0.5
        elif i==3:
            scor+=x*0.25
        elif i==4:
            scor+=x*0.15

    percentage = ctrl.Antecedent(np.arange(0, 100, 1), 'percentage')
    score = ctrl.Antecedent(np.arange(0, 5,1), 'score')
    res = ctrl.Consequent(np.arange(0, 5 ,1), 'res')
    percentage.automf(3)
    score.automf(3)
    res['low'] = fuzz.trimf(res.universe, [0, 0, 2])
    res['medium'] = fuzz.trimf(res.universe, [0, 2, 4])
    res['high'] = fuzz.trimf(res.universe, [2, 4, 4])
    rule1 = ctrl.Rule(percentage['poor'] | score['poor'], res['low'])
    rule2 = ctrl.Rule(percentage['average']| score['average'], res['medium'])
    rule3 = ctrl.Rule(percentage['good'] | score['good'], res['high'])
    res_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
    result = ctrl.ControlSystemSimulation(res_ctrl)
    result.input['percentage'] = percent
    result.input['score'] = scor
    result.compute()
    return result.output['res']


def upload_image(mail):
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(filename)
        print(filename)
        imageFile = open(filename, 'rb')
        z = base64.b64encode(imageFile.read())
        print("encrypted")
        connection = MongoClient("mongodb+srv://Akash_Lo-kiB:3HvOrW2YS2O0Ksnf@cluster0.awzi6.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority")
        db = connection['Lo-KiB']
        collection = db['institute_details']
        collection.update_one({'mail': mail}, {"$push": {'image': z}})
        print("stored")
        imageFile.close()
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)

def upload_certificate(mail):
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(filename)
        imageFile = open(filename, 'rb')
        z = base64.b64encode(imageFile.read())
        connection = MongoClient("mongodb+srv://Akash_Lo-kiB:3HvOrW2YS2O0Ksnf@cluster0.awzi6.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority")
        db = connection['Lo-KiB']
        collection = db['student_details']
        collection.update_one({'mail': mail}, {"$push": {'image': z}})
        imageFile.close()
    else:
        flash('Allowed image types are -> png, jpg, jpeg, gif')
        return redirect(request.url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        global k
        email = request.form.get('emailid')
        k = email
        password_input = request.form.get('password')
        details = validate_user(email)
        if details:
            if details[1] == 'Student' and check_password_hash(details[0], password_input):
                return redirect(url_for('stud_home'))
            elif details[1] == 'College' and check_password_hash(details[0], password_input):

                return redirect(url_for('coll_home'))
            else:
                flash('Login Unsuccessful. Please check email and password')
        else:
            flash('Login Unsuccessful. Please check email and password')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        choice = request.form.get('radiob')
        username=request.form.get('UserName')
        email = str(request.form.get('emailid'))
        passw = request.form.get('password')
        confirm = request.form.get('cpassword')
        if passw == confirm:
            register_user(email, username, passw, choice)
            return redirect(url_for('login'))
        else:
            flash("Your credentials does not match,Try again")
    return render_template('signup.html')


@app.route('/school_details', methods=['GET', 'POST'])
def school_register():
    if request.method == "POST":
        name = request.form.get('sc_name')
        mail = request.form.get('mail')
        addr = request.form.get('address')
        contact = request.form.get('contact')
        amenity = request.form.get('amenity')
        pin = request.form.get('pin')
        state = request.form.get('state')
        country = request.form.get('country')
        upload_image(mail)
        board = request.form.get('board')
        uniid = request.form.get('uni_ID')
        courses = request.form.get('courses')
        fees = request.form.get('fee')
        save_school_details(name, mail, addr, country, contact, amenity, pin, state, board, uniid, courses, fees)
        try:
            upload_image(mail)
        except:
            pass
        flash("your details have been stored successfully.Check out our pricing for better usage")
    return render_template('school_details.html')


@app.route('/college_details', methods=['GET', 'POST'])
def college_register():
    if request.method == "POST":
        name = request.form.get('name')
        mail = request.form.get('email')
        addr = request.form.get('address')
        contact = request.form.get('phoneno')
        amenity = request.form.get('amenities')
        pin = request.form.get('pin')
        state = request.form.get('state')
        country = request.form.get('country')
        board = request.form.get('board')
        uniid = request.form.get('uni_ID')
        courses = request.form.get('courses')
        fees = request.form.get('fee')
        save_college_details(name, mail,addr,country,contact,amenity,pin,state,board,uniid,courses,fees)
        try:
            upload_image(mail)
        except:
            pass
        flash("your details have been stored successfully.Check out our pricing for better usage")
    return render_template('coll_details.html')


@app.route('/collegehome', methods=['GET', 'POST'])
def coll_home():
    if request.method == 'POST':
        type = request.form.get('Type')
        if type == 'school':
            return redirect(url_for('school_register'))
        else:
            return redirect(url_for('college_register'))
    return render_template('coll_index.html')


@app.route('/college_req', methods=['GET', 'POST'])
def coll_require():
    if request.method == "POST":
        sc_name = request.form.get('ins_name')
        percentage = request.form.get('percetage')
        seats = request.form.get('seats')
        last_date = request.form.get('last_date')
        bank = request.form.get('bank')
        sc_requirement_update(sc_name, percentage, seats, last_date, bank)
        flash("your details have been stored successfully.Check out our pricing for better usage")
    return render_template('college_req.html')


@app.route('/pricing', methods=['GET', 'POST'])
def pricing():
    return render_template('payment.html')

@app.route('/create_website', methods=['GET','POST'])
def create_website():
    return render_template('website.html')

@app.route('/register_student', methods=['GET', 'POST'])
def stud_register():
    global k
    if request.method == 'POST':
        f_name = request.form.get('First_Name')
        l_name = request.form.get('Last_Name')
        email = request.form.get('emailid')
        dob=request.form.get('dob')
        mobile = request.form.get('Mobile_Number')
        gender = request.form.get('Gender')
        address = request.form.get('Address')
        city=request.form.get('City')
        pin = request.form.get('Pin_Code')
        state = request.form.get('State')
        country = request.form.get('Country')
        documents = request.form.get('drive')
        previous_class = request.form.get('Class')
        previous_school = request.form.get('school')
        previous_score = request.form.get('percentage')
        previous_year = request.form.get('year')
        save_student_details(f_name,l_name,email,dob,mobile,gender,address,city,pin,state,country,documents,previous_class,previous_school,previous_score,previous_year)
        t=[]
        n=request.form.get('national')
        try:
            if n==None:
                pass
            else:
                t.append(n)
            s=request.form.get('state')
            if s == None:
                pass
            else:
                t.append(s)
            d=request.form.get('district')
            if d == None:
                pass
            else:
                t.append(d)
            t=request.form.get('taluk')
            if t == None:
                pass
            else:
                t.append(t)
            h=request.form.get('hobli')
            if h == None:
                pass
            else:
                t.append(h)
            va=calculate(80,t)
            print(va)
            acheivement_save(email,va)
        except:
            pass
        flash('registration successfull')
        return redirect(url_for('stud_home'))
    return render_template('student_details.html', k=k)


@app.route('/studenthome', methods=['GET', 'POST'])
def stud_home():
    h=bool(check_student(k))
    coll_list,j = get_colleges()
    o=list(range(j))
    sol = zip(coll_list,o)

    return render_template('stud_index.html', incomplete=not(h),list_col=sol)


@app.route('/selection/<inst_name>', methods=['GET', 'POST'])
def selection_page(inst_name):
    print(inst_name)
    details=collegedetails(inst_name)
    if request.method == 'POST':
        st=studentdetails(k)
        email = details['mail']
        with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login('vrujeshhm.lokib@gmail.com', 'Vruje@230620')
            name=st['name']
            dob=st['dob']
            mail=st['mail']
            contact=st['contact detail']
            gender=st['gender']
            address=st['address']
            city=st['city']
            pin=st['pincode']
            state=st['state']
            country=st['country']
            drive=st['drive_link']

            precl=st['previous_class']
            presch=st['previous_school']
            presco=st['previous_score']
            preyr=st['previous_year']

            subject = 'Admission application'
            body =str(name) + "\n"+ str(mail)+ "\n"+ str(dob)+ "\n"+ str(contact)+ "\n"+ str(gender)+ "\n"+ str(address)+ "\n"+ str(city)+ "\n"+ str(pin)+ "\n"+ str(state) + "\n"+ str(country)+ "\n"+ str(drive)+ "\n"+ str(precl)+ "\n"+ str(presch)+ "\n"+ str(presco)+ "\n"+ str(preyr)+\
        """
        has registered to your School/college.
        we request you to send him confirmation mail and provide info on regarding the payment details.


        Thank you

        Best Regards
        Team Lo-KiB

        """
            msg = f'Subject: {subject}\n\n {body}'
            smtp.sendmail('vrujeshhm.lokib@gmail.com', email, msg)
            flash('Mail has been Sent')

    return render_template('college_student.html',details=details)


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        choice = request.form.get('radiob')
        email = request.form.get('emailid')
        url = request.host_url + 'reset_password'
        if get_email(email, choice):
            with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login('vrujeshhm.lokib@gmail.com', 'Vruje@230620')
                expires = return_expiry_time()
                unique_code = create_access_token(str(email), expires_delta=expires)
                subject = 'Reset your Password for Lo-KiB tech'
                body = f'To reset your password, click on the link below: \n {url}/{unique_code} \n\n This link will expire in 5 minutes!! \n'
                msg = f'Subject: {subject}\n\n {body}'
                smtp.sendmail('vrujeshhm.lokib@gmail.com', email, msg)
                flash('Mail has been Sent')
        else:
            flash('Enter a valid E-mail address')
    return render_template('forgot.html')


@app.route('/reset_password/<code>', methods=['GET', 'POST'])
def reset_password(code):
    user_mail = decode_token(code)['identity']
    if request.method == 'POST':
        password_1 = request.form.get('password_1')
        password_2 = request.form.get('password_2')
        if password_1 == password_2:
            update_password(user_mail, password_1)
            flash('Password changed successfully')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match')
    return render_template('resetpassword.html')


if __name__ == '__main__':
    app.run(debug=True)
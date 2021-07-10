from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
import smtplib
from flask_jwt_extended import create_access_token, decode_token, JWTManager
from return_time import return_expiry_time
from db import register_user, validate_user, get_email, update_password,save_student_details,sc_requirement_update,save_college_details,save_school_details
from pymongo import MongoClient
from werkzeug.utils import secure_filename

import base64
app = Flask(__name__)
app.secret_key = 'Hack@utsav'
jwt = JWTManager(app)

PEOPLE_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def first():
    return render_template('welcome.html')

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
        imageFile = open(filename, 'rb')
        z = base64.b64encode(imageFile.read())
        connection = MongoClient("mongodb+srv://Akash_Lo-kiB:3HvOrW2YS2O0Ksnf@cluster0.awzi6.mongodb.net/test?ssl=true&ssl_cert_reqs=CERT_NONE&retryWrites=true&w=majority")
        db = connection['Lo-KiB']
        collection = db['institute_details']
        collection.update_one({'mail': mail}, {"$push": {'image': z}})
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
        email = request.form.get('emailid')
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
        username=request.form.get('Username')
        email = str(request.form.get('emailid'))
        passw = request.form.get('password')
        confirm = request.form.get('cpassword')
        if passw == confirm:
            register_user(email, username, passw, choice)
            return redirect(url_for('login'))
        else:
            flash("Your credentials does not match,Try again")
    return render_template('signup.html')



@app.route('/collegehome', methods=['GET', 'POST'])
def coll_home():
    if request.method == 'POST':
        type = request.form.get('Type')
        if type=='school':
            return redirect(url_for(school_register))
        else:
            return redirect(url_for(college_register))
    return render_template('coll_index.html')


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
        try:
            upload_image(mail)
        except:
            pass
        board = request.form.get('board')
        uniid = request.form.get('uni_ID')
        courses = request.form.get('courses')
        fees = request.form.get('fee')
        save_college_details(name, mail, addr, country, contact, amenity, pin, state, board, uniid, courses, fees)
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
        try:
            upload_image(mail)
        except:
            pass
        board = request.form.get('board')
        uniid = request.form.get('uni_ID')
        courses = request.form.get('courses')
        fees = request.form.get('fee')
        save_college_details(name, mail,addr,country,contact,amenity,pin,state,board,uniid,courses,fees)
        flash("your details have been stored successfully.Check out our pricing for better usage")
        return redirect(url_for(coll_home))
    return render_template('coll_details.html')


@app.route('/college_req', methods=['GET', 'POST'])
def coll_require():
    if request.method == "POST":
        sc_name = request.form.get('ins_name')
        percentage = request.form.get('percetage')
        seats = request.form.get('seats')
        last_date = request.form.get('last_date')
        bank = request.form.get('bank')
        sc_requirement_update(sc_name,percentage,seats,last_date,bank)
    return render_template('college_req.html')


@app.route('/pricing', methods=['GET', 'POST'])
def pricing():
    return render_template('payment.html')


@app.route('/studenthome', methods=['GET', 'POST'])
def stud_home():
    return render_template('stud_index.html')


@app.route('/register_student', methods=['GET', 'POST'])
def stud_register():
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
        achievement = request.form.get('Username')
        previous_class = request.form.get('Class')
        previous_school = request.form.get('school')
        previous_score = request.form.get('percentage')
        previous_year = request.form.get('year')

        if request.form.get('national'):
            n=1
            try:
                upload_certificate(email)
            except:
                pass
        if request.form.get('state'):
            s=1
            try:
                upload_certificate(email)
            except:
                pass
        if request.form.get('district'):
            d=1
            try:
                upload_certificate(email)
            except:
                pass
        if request.form.get('taluk'):
            t=1
            try:
                upload_certificate(email)
            except:
                pass
        if request.form.get('hobli'):
            h=1
            try:
                upload_certificate(email)
            except:
                pass
        save_student_details(f_name,l_name,email,dob,mobile,gender,address,city,pin,state,country,achievement,previous_class,previous_school,previous_score,previous_year)
        selection_page(email)

    return render_template('student_details.html')

@app.route('/selelction', methods=['GET', 'POST'])
def selection_page(mail):
    return render_template('student_home.html',mail=mail)


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

@app.route('/logout',  methods=['GET', 'POST'])
def logout():
    return redirect(url_for(first))

if __name__ == '__main__':
    app.run(debug=True)
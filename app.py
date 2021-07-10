from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
import smtplib
from flask_jwt_extended import create_access_token, decode_token, JWTManager
from return_time import return_expiry_time
from db import register_user, validate_user, get_email, update_password

app = Flask(__name__)
app.secret_key = 'Hack@utsav'
jwt = JWTManager(app)

@app.route('/')
def first():
    return render_template('welcome.html')


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


@app.route('/studenthome', methods=['GET', 'POST'])
def stud_home():
    return render_template('stud_index.html')


@app.route('/collegehome', methods=['GET', 'POST'])
def coll_home():
    return render_template('coll_index.html')

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
        #save_student_details()

    return render_template('student_details.html')



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

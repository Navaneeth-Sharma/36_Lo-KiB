from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash

from db import register_user, validate_user, get_username
app = Flask(__name__)
app.secret_key = 'Hack@utsav'


@app.route('/')
def first():
    return render_template('welcome.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('emailid')
        password_input = request.form.get('password')
        details=validate_user(email)
        if details[1] == 'Student' and check_password_hash(details[0], password_input):
            return redirect(url_for('stud_home'))
        elif details[1] == 'College' and check_password_hash(details[0], password_input):
            return redirect(url_for('coll_home'))
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
    return render_template('index.html')


@app.route('/collegehome', methods=['GET', 'POST'])
def coll_home():
    return render_template('index.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    return render_template('forgot.html')

@app.route('/reset', methods=['GET', 'POST'])
def forgot():
    return render_template('resetpassword.html')

if __name__ == '__main__':
    app.run(debug=True)

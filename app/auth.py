from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import User, db

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists!')
            return redirect(url_for('auth.register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            # Default profile picture
            session['profile_pic'] = user.profile_pic or 'default.jpg'

            flash("Logged in successfully!", "success")
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password!', "danger")
            return redirect(url_for('auth.login'))
    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', "success")
    return redirect(url_for('main.home'))

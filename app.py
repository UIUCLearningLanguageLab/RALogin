from flask import Flask
from flask import render_template, flash, redirect
from forms import LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user

from config import Config
from user import User

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.user_name.data == 'ra' and form.password.data == 'ra':
            user = User(id=form.user_name.data)
            login_user(user)
            flash('login successful')
            return redirect('index')
    return render_template('login.html', form=form)


@app.route("/settings")
@login_required
def settings():
    pass


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('index')


@login_required
@app.route('/menu')
def menu():
    return render_template('index.html')
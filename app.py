from flask import Flask, session
from flask import render_template, flash, redirect
from forms import LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user

from config import Config
from user import User

from utils import make_image_comparison_html

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
    image_list = ['yg1_rr.jpg']  # todo dynamic

    return render_template('index.html', image_list=image_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.user_name.data == 'ra' and form.password.data == 'ra':  # TODO get environment variable
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


@login_required
@app.route('/image-comparison')
def image_comparison():

    return 'Not implemented yet'

    user = session['user_id']

    if user.id == 'ra':
        target_folders = ['andrew', 'layla']
    else:
        raise AttributeError('NO matching user.id')

    target_image = ''  # TODO dynamic
    html = make_image_comparison_html(target_folders, target_image)  # TODO

    return html

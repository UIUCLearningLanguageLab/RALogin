from flask import Flask, session, request
from flask import render_template, flash, redirect
from forms import LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user

from superannotate.exceptions import SABaseException

import configs
from user import User
from utils import make_image_comparison_html

app = Flask(__name__)
app.config.from_object(configs.FlaskApp)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
@app.route('/index')
def index():

    try:
        user_id = session['_user_id']
    except KeyError:
        return 'Did not find _user_id in session'
    else:
        user = User.get(user_id)

    if user.id == 'ra':
        ra_list = ['andrew', 'layla']
    if user.id == 'yushang4@illinois.edu':
        ra_list = ['gotoole2@illinois.edu',
                   'mstill2@illinois.edu',
                   'ppaun2@illinois.edu', 
                   'julieyc3@illinois.edu']
    if user.id == 'tkoropp2@illinois.edu':
        ra_list = ['mtam6@illinois.edu', 
                   'janayf2@illinois.edu',
                   'acw4@illinois.edu', 
                   'tyzhao2@illinois.edu']
    if user.id == 'dharve5@illinois.edu':
        ra_list = ['laylaic2@illinois.edu', 
                   'mstill2@illinois.edu',
                   'karenmn2@illinois.edu', 
                   'asevers2@illinois.edu']
    else:
        raise AttributeError('No matching user.id')

    #name of the project
    project = 'training_sets_headcam'
    image_list = []

    #for ra in ra_list download metadata as list of dictionary (one dictionary per image)

    for ra in ra_list:
        image_dict_list = sa.search_images(project + '/' + ra, image_name_prefix=None, annotation_status=None, return_metadata=True)
        #for image dictionary in list of dicitonary add image name to list
        for diction in image_dict_list:
            if diction['name'] not in image_list:
                image_list.append(diction['name'])

    # image_list = ['yg1_rr.jpg', 'test']  # todo dynamic

    return render_template('index.html', image_list=image_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():

        try:
            correct_pw = configs.Authentication.user2pw[form.user_name.data]  # TODO get pw from environment variable
        except KeyError:
            flash('Did not recognize user name.')
            return redirect('index')
        else:
            if form.password.data == correct_pw:
                user = User(id=form.user_name.data)
                login_user(user)
                flash('Login successful.')
                return redirect('index')
            else:
                flash('Incorrect password.')
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
@app.route('/image-comparison')
def image_comparison():

    # get requested image file name
    target_image = request.args['image_dropdown']

    try:
        user_id = session['_user_id']
    except KeyError:
        return 'Did not find _user_id in session'
    else:
        user = User.get(user_id)

    try:
        html_elements = make_image_comparison_html(target_folders, target_image)
    except SABaseException as e:
        msg = ''
        msg += '<h2 style="color: red;">Failed to produce HTML due to error in superannotate:</h2>'
        msg += '<br>'
        msg += e.message
        return msg
    else:
        return render_template('image_comparison.html', target_image=target_image, **html_elements)

from flask import Flask, session, request
from flask import render_template, flash, redirect
from forms import LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user
import superannotate as sa

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


def get_ra_list(user: User):
    if user.id == 'ra':
        return ['andrew',
                'layla']
    elif user.id == 'yushan':
        return ['graceo',
                'miranda',
                'pavel',
                'julie']
    elif user.id == 'tom':
        return ['michelle',
                'janay',
                'arianna',
                'talia']
    elif user.id == 'danaizha':
        return ['layla',
                'karen',
                'andrews']
    else:
        raise AttributeError('No matching user.id')


@login_required
@app.route('/menu')
def menu():
    """
    this is the page that is returned after a user is logged in.
    here they can perform whatever functions are available (i.e. pick images to compare rom dropdown).
    """
    try:
        user_id = session['_user_id']
    except KeyError:
        return 'Did not find _user_id in session'
    else:
        user = User.get(user_id)

    ra_list = get_ra_list(user)

    # name of the project
    project = 'training_sets_headcam'
    image_list = []

    # necessary before using any superannotate functionality
    sa.init(configs.Paths.superannotate_config_path)

    # for ra in ra_list download metadata as list of dictionary (one dictionary per image)
    for ra in ra_list:

        print(f'Searching images for ra={ra}')

        project = project + '/' + ra  # todo is this right?
        image_name_prefix = ''
        annotation_status = ''
        assert image_name_prefix and annotation_status
        try:
            image_dict_list = sa.search_images(project, image_name_prefix, annotation_status, return_metadata=True)
        except SABaseException as e:
            msg = ''
            msg += '<h2 style="color: red;">Failed to produce HTML due to error in superannotate:</h2>'
            msg += '<br>'
            msg += e.message
            return msg

        # for image dictionary in list of dictionary add image name to list
        for diction in image_dict_list:
            if diction['name'] not in image_list:
                image_list.append(diction['name'])

    return render_template('menu.html', image_list=image_list)


@app.route('/')
@app.route('/index')
def index():

    return render_template('index.html')


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
                return redirect('menu')
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

    target_folders = get_ra_list(user_id)
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

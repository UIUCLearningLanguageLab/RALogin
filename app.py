from flask import Flask, session, request
from flask import render_template, flash, redirect
from forms import LoginForm
from flask_login import LoginManager, login_user, login_required, logout_user
import superannotate as sa
from dotenv import dotenv_values

from superannotate.exceptions import SABaseException

import configs
from user import User
from utils import make_image_comparison_html, find_target_folders

app = Flask(__name__)
app.config.from_object(configs.FlaskApp)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@login_required
@app.route('/menu')
def menu():
    """
    this is the page that is returned after a user is logged in.
    here they can perform whatever functions are available (i.e. pick images to compare rom dropdown).
    """

    # remove previously downloaded data
    for path in configs.Paths.downloads.glob('*'):
        print(f'Removing {path}')
        path.unlink()

    # necessary before using any superannotate functionality
    sa.init(str(configs.Paths.superannotate_config_path))

    try:
        image_names = sa.search_images_all_folders(configs.ImageComparison.project)
    except SABaseException as e:
        msg = ''
        msg += '<h2 style="color: red;">Failed to produce HTML due to error in superannotate:</h2>'
        msg += '<br>'
        msg += e.message
        return msg
    else:
        image_names = sorted(set(image_names))

    return render_template('menu.html', image_names=image_names)


@app.route('/')
@app.route('/index')
def index():

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            env = dotenv_values('.env')
            correct_pw = env[form.user_name.data]
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

    target_folders = find_target_folders(target_image, user)

    try:
        html_elements = make_image_comparison_html(target_folders, target_image)
    except SABaseException as e:
        msg = ''
        msg += '<h2 style="color: red;">Failed to produce HTML due to error in superannotate:</h2>'
        msg += '<br>'
        msg += e.message
        msg += f'<br>Using target_folders={target_folders} and target_image={target_image}'
        return msg
    except FileNotFoundError as e:
        msg = ''
        msg += '<h2 style="color: red;">Failed to produce HTML because a file was not downloaded by superannotate:</h2>'
        msg += '<br>'
        msg += e.filename
        msg += f'<br>Using target_folders={target_folders} and target_image={target_image}'
        return msg

    if not html_elements:
        flash(f'Did not find annotation data for {target_image}')

    return render_template('image_comparison.html',
                           target_image=target_image,
                           is_target_image_downloaded=True if html_elements else False,
                           **html_elements)



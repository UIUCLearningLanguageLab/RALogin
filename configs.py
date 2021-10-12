from pathlib import Path


class Authentication:
    user2pw = {'ra': 'ra'}


class Paths:
    cwd = Path.cwd()
    superannotate_config_path = cwd / 'superannotate_config.json'
    downloads = Path('downloads')
    assert downloads.exists()


class FlaskApp(object):
    SECRET_KEY = '39hsagshgggb'


from pathlib import Path


class Authentication:
    user2pw = {'ra': 'ra',
               'yushang4@illinois.edu': '003imageSemantics',
               'tkoropp2@illinois.edu': '002imageSemantics',
               'dharve5@illinois.edu': '001imageSemantics'}


class Paths:
    root = Path(__file__).parent
    superannotate_config_path = root / 'superannotate_config.json'
    downloads = Path('static/downloads')
    assert downloads.exists()


class FlaskApp(object):
    SECRET_KEY = '39hsagshgggb'


class ImageComparison:
    project = 'training_sets_headcam'

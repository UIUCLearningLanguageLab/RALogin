from pathlib import Path


class Paths:
    root = Path(__file__).parent
    superannotate_config_path = root / 'superannotate_config.json'
    downloads = Path('static/downloads')
    assert downloads.exists()


class FlaskApp(object):
    SECRET_KEY = '39hsagshgggb'


class ImageComparison:
    project = '2022-4fall_training_sets'
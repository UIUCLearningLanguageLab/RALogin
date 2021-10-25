from pathlib import Path


class Authentication:
    user2pw = {'ra': 'ra',
               'yushang4@illinois.edu': '003imageSemantics',
               'tkoropp2@illinois.edu': '002imageSemantics',
               'dharve5@illinois.edu': '001imageSemantics',

                'laylaic2@illinois.edu': 'iS38481235',
                'karenmn2@illinois.edu': 'iS38481545',
                'asevers2@illinois.edu': 'iS38481532',

                'janayf2@illinois.edu': 'iS38481531',
                'acw4@illinois.edu': 'iS38481599',
                'mtam6@illinois.edu': 'iS38481563',
                'tyzhao2@illinois.edu': 'iS38481999',

                'mstill2@illinois.edu': 'iS38481888',
                'julieyc3@illinois.edu': 'iS38481347',
                'ppaun2@illinois.edu': 'iS38481282',
                'gotoole2@illinois.edu': 'iS38481100'}

class Paths:
    root = Path(__file__).parent
    superannotate_config_path = root / 'superannotate_config.json'
    downloads = Path('static/downloads')
    assert downloads.exists()


class FlaskApp(object):
    SECRET_KEY = '39hsagshgggb'

class ImageComparison:
    project = 'training_sets_headcam'
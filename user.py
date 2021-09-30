from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id: str):
        self.id = id

    @classmethod
    def get(cls, user_id: str):
        if user_id == 'ra':
            return cls(id='ra')

        return None

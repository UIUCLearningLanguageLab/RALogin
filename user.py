from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id: str):
        self.id = id

    @classmethod
    def get(cls, user_id: str):

        # this can be made more flexible. as of now, a user name is the user's id.
        return cls(id=user_id)


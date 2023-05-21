from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.password = password

    def check_password(self, password):
        """
        Check if the provided password matches the user's password
        :param password: the password to check
        :return: True if the password matches, False otherwise
        """
        return self.password == password


class UserCreationDTO():
    def __init__(self, email, password, role, share_cod, high_value=None, low_value=None):
        self.email = email
        self.password = password
        self.role = role
        self.share_cod = share_cod
        self.high_value = high_value
        self.low_value = low_value
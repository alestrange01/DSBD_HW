
class UserCreationDTO():
    def __init__(self, email, password, role, share_cod, high_value=None, low_value=None):
        self.email = email
        self.password = password
        self.role = role
        self.share_cod = share_cod
        self.high_value = high_value
        self.low_value = low_value
    
    def __repr__(self):
        return f"UserCreationDTO(email={self.email}, password={self.password}, role={self.role}, share_cod={self.share_cod}, high_value={self.high_value}, low_value={self.low_value})"

class UserUpdateDTO():
    def __init__(self, email, password, share_cod, high_value=None, low_value=None):
        self.email = email
        self.password = password
        self.share_cod = share_cod
        self.high_value = high_value
        self.low_value = low_value
    
    def __repr__(self):
        return f"UserUpdateDTO(email={self.email}, password={self.password}, share_cod={self.share_cod}, high_value={self.high_value}, low_value={self.low_value})"
    
class UserDTO():
    def __init__(self, email, role, share_cod, high_value=None, low_value=None):
        self.email = email
        self.role = role
        self.share_cod = share_cod
        self.high_value = high_value
        self.low_value = low_value
    
    def __repr__(self):
        return f"UserDTO(email={self.email}, role={self.role}, share_cod={self.share_cod}, high_value={self.high_value}, low_value={self.low_value})"
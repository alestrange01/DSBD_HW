
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
    def __init__(self, email, new_share_cod, new_high_value=None, new_low_value=None):
        self.email = email
        self.new_share_cod = new_share_cod
        self.new_high_value = new_high_value
        self.new_low_value = new_low_value
    
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
    
    def to_dict(self):
        return {
            "email": self.email,
            "role": self.role,
            "share_cod": self.share_cod,
            "high_value": float(self.high_value) if self.high_value is not None else None,
            "low_value": float(self.low_value) if self.low_value is not None else None
        }
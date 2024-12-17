class UserDTO:
    def __init__(self, email: str, share_cod: str, high_value: float, low_value: float):
        self.email = email
        self.share_cod = share_cod
        self.high_value = high_value
        self.low_value = low_value

    def __repr__(self):
        return f"<UserDTO: email='{self.email}', share_cod='{self.share_cod}', high_value={self.high_value}, low_value={self.low_value})>"
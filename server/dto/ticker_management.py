class TickerManagementUpsertDTO:
    def __init__(self, share_cod, counter=1):
        self.share_cod = share_cod
        self.counter = counter

    def __repr__(self):
        return f"TickerManagementUpsertDTO(share_cod={self.share_cod}, counter={self.counter})"

class TickerManagementDTO:
    def __init__(self, share_cod, counter):
        self.share_cod = share_cod
        self.counter = counter

    def __repr__(self):
        return f"TickerManagementDTO(share_cod={self.share_cod}, counter={self.counter})"
    
    def to_dict(self):
        return {
            "share_cod": self.share_cod,
            "counter": self.counter
        }
    

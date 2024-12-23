class TickerManagementDTO:
    def __init__(self, share_cod, counter):
        self.share_cod = share_cod
        self.counter = counter

    def __repr__(self):
        return f"<TickerManagementDTO: share_cod='{self.share_cod}', counter={self.counter})>"
class TickeManagementDTO: 
    def __init__(self, share_cod):
        self.share_cod = share_cod
        
    def __repr__(self):
        return f"<TickerManagementDTO: share_cod='{self.share_cod}')>"

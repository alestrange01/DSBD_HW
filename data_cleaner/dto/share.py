class ShareDTO:
    def __init__(self, id, timestamp):
        self.id = id
        self.timestamp = timestamp
        
    def __repr__(self):
        return f"<ShareDTO: id={self.id}, timestamp={self.timestamp})>"
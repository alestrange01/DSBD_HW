class ShareDTO():
    def __init__(self, share_name, value, timestamp):
        self.share_name = share_name
        self.value = value
        self.timestamp = timestamp
    
    def __repr__(self):
        return f"ShareDTO(share_name={self.share_name}, value={self.value}, timestamp={self.timestamp})"
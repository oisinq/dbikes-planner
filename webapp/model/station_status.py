class StationStatus:
    number_of_bikes = -1
    timestamp = -1 

    def __init__(self, number_of_bikes, timestamp):
        self.number_of_bikes = number_of_bikes
        self.timestamp = timestamp
    
    def __str__(self):
        return f"num bikes: {self.number_of_bikes}, timestamp: {self.timestamp}"
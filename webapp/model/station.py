class Station:
    statuses = []

    def __init__(self, name):
        self.name = name

    def add_status(self, status):
        self.statuses.append(status)

    def latest_status(self):
        return self.statuses[-1]

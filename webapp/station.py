class Station:
    statuses = []
    name = ''

    def __init__(self, name):
        self.name = name

    def add_status(self, status):
        self.statuses.append(status)

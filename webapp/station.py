class Station:
    statuses = []

    def __init__(self, name):
        self.name = name

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self, value):
        self._name = value

    def add_status(self, status):
        self.statuses.append(status)

    def latest_status(self):
        return self.statuses[-1]

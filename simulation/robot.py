class Robot:
    def __init__(self, id):
        self.id = id
        self.position = (0, 0)

    def move(self, dx, dy):
        self.position = (self.position[0] + dx, self.position[1] + dy)

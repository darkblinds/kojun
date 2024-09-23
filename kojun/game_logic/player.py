class Player:
    def __init__(self, name : str):
        self.loser = False
        self.turn = False
        self.name = name

    def enable(self):
        self.turn = True
    
    def disable(self):
        self.turn = False

    def setLoser(self):
        self.loser = True

    def reset(self):
        self.loser = False
        self.turn = False
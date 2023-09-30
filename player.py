import random

class Player:
    def __init__(self, name, actions):
        self.name = name
        self.choices = actions

    def make_choice(self):
        return random.choice(self.choices)
    
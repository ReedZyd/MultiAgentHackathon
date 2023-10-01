import random

class Player:
    def __init__(self, name, n_players, actions=None):
        self.name = name
        if actions is None:
            actions = ['cooperate', 'betray']
        self.choices = actions
        self.n_players = n_players

    def get_action(self):
        return random.choice(self.choices)
    
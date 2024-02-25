class PrisonersDilemma3:
    def __init__(self, num_players=3):
        self.num_players = num_players
        self.points = [0,1,3,5,7,9]
        self.payoff_matrix = {('cooperate', 'cooperate', 'cooperate'): [self.points[4], self.points[4], self.points[4]],
                              ('cooperate', 'cooperate', 'defect'): [self.points[2], self.points[2], self.points[5]],
                              ('cooperate', 'defect', 'cooperate'): [self.points[2], self.points[5], self.points[2]],
                              ('cooperate', 'defect', 'defect'): [self.points[0], self.points[3], self.points[3]],
                              ('defect', 'cooperate', 'cooperate'): [self.points[5], self.points[2], self.points[2]],
                              ('defect', 'cooperate', 'defect'): [self.points[3], self.points[0], self.points[5]],
                              ('defect', 'defect', 'cooperate'): [self.points[3], self.points[3], self.points[0]],
                              ('defect', 'defect', 'defect'): [self.points[1], self.points[1], self.points[1]]}
        self.actions = []
        self.scores = [0] * num_players

    def make_choice(self,choice):
        """玩家做出选择: 'cooperate' 或 'defect'"""
        if choice not in ['cooperate', 'defect']:
            raise ValueError("Choice must be 'cooperate' or 'defect'")
        self.actions.append(choice) # the players should be taking actions in the same order

    def calculate_scores(self):
        """计算每个玩家的得分"""
        score_list = self.payoff_matrix[tuple(self.actions)]
        return score_list
    
    def clear_actions(self):
        """清除所有玩家的选择"""
        self.actions = []
    def get_scores(self):
        """返回每个玩家的得分"""
        return self.scores

    def reset(self):
        """重置游戏"""
        self.actions = []
        self.scores = [0] * self.num_players

if  __name__ == '__main__':
    env = PrisonersDilemma3()
    env.make_choice('cooperate')
    env.make_choice('cooperate')
    env.make_choice('cooperate')
    print(env.actions)
    print(env.calculate_scores())
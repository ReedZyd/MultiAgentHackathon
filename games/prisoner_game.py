class PrisonersDilemma:
    def __init__(self, num_players, points):
        self.num_players = num_players
        self.points = points
        self.actions = []
        self.scores = [0] * num_players

    def make_choice(self, player_id, choice):
        """玩家做出选择: 'cooperate' 或 'defect'"""
        if choice not in ['cooperate', 'defect']:
            raise ValueError("Choice must be 'cooperate' or 'defect'")
        self.actions.append((player_id, choice))

    def calculate_scores(self):
        """计算每个玩家的得分"""
        defect_count = sum(1 for _, choice in self.actions if choice == 'defect')
        score_list = []
        for player_id, choice in self.actions:
            if choice == 'cooperate':
                if defect_count == 0:
                    score = self.points[2] # all cooperate
                else:
                    score = self.points[4] # cooperate while any of the others defect
            else:
                if defect_count == 1:
                    score = self.points[0] # defect while others cooperate
                elif defect_count == self.num_players:
                    score = self.points[3] # all defect
                else:
                    score = self.points[1] # more than 1 defect
            self.scores[player_id] += score
            score_list.append(score)
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


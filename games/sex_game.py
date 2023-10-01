class BattleOfSexes3:
    def __init__(self):

        # 定义action序列
        self.actions = ['A', 'B']
        # 定义payoff矩阵
        # 假设payoff矩阵如下：
        # 如果三人都选择看足球比赛，payoff为(2, 2, 2)
        # 如果三人都选择看歌剧，payoff为(1, 1, 1)
        # 其他情况，payoff为(0, 0, 0)
        # self.payoff_matrix = {
        #     ('Football', 'Football', 'Football'): (2, 2, 2),
        #     ('Opera', 'Opera', 'Opera'): (1, 1, 1),
        # }
        self.payoff_matrix = {
            ('A', 'Football', 'A'): (2, 0, 2),
            ('Opera', 'Opera', 'Opera'): (1, 1, 1),
        }

    def print_payoff_matrix(self):
        for key, value in self.payoff_matrix.items():
            print(f"Choices: {key} -> Payoff: {value}")

    def find_nash_equilibrium(self):
        # 在这个简单的例子中，纳什均衡是三人都选择看足球比赛或三人都选择看歌剧
        return [('Football', 'Football', 'Football'), ('Opera', 'Opera', 'Opera')]

    def get_payoff(self, choices):
        return self.payoff_matrix.get(choices, (0, 0, 0))
    
    def get_actions(self):
        return self.actions

# # 使用
# game = BattleOfSexes3()
# game.print_payoff_matrix()
# nash_equilibria = game.find_nash_equilibrium()
# print(f"Nash Equilibria: {nash_equilibria}")
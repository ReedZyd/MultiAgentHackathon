
from games.prisoner_game import PrisonersDilemma
from player import Player
import openai
import time
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import trange
import pandas as pd
import numpy as np


GPT_VERSION = "gpt-3.5-turbo"
# GPT_VERSION = "gpt-4"

class LLMPlayer(Player):

    def chatgpt_api_simulation(self, prompt, stop=["\n"]):
        # 这是一个模拟的API函数，它返回一个随机选择。
        # 在真实的实现中，这里应该是与ChatGPT的真实交互。
        i = 2
        while True:
            try:
                # time.sleep(1)
                completion = openai.ChatCompletion.create(
                    model=GPT_VERSION,
                    messages=[
                        {"role": "system", "content": "You are a player involved in the 'Prisoner's Dilemma' game.\n\n"},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                    top_p=0.5,
                )
                # print(completion.choices[0])
                return completion.choices[0].message['content']
            except:
                # num_tokens = num_tokens(prompt)

                i = i * 2
                print("Error in LLM, sleep seconds: ", i)
                time.sleep(i)
                if i > 128:
                    return {'content': ''}


    def get_action(self, points=None, num_turn=[1, 1], action_history=None, score_history=None, print_flag=True):
        def get_des_from_payoff_matrix(points):
            re  = "1. As a player, you can choose from: 'cooperate', 'defect'.\n"
            # re += f"2. If all players choose to cooperate, each of us earns {points[1]} points.\n"
            # re += f"3. If all players choose to defect, each of us gets {points[2]}  point.\n"
            # re += f"4. If you choose to defect while all of others choose to cooperate, then you earn {points[0]} points, while those who cooperate get {points[3]} point.\n"
            # re += f"5. If you choose to cooperate while any of others choose to defect, then you earn {points[3]} point, others who defect earn {points[0]}  points.\n"
            re  += "2. Remember your goal is to maximize your own payoff. "
            re += "You should only care about your own interests.\n"
            # re  += "2. Your goal is to find an action that is the best to the actions of the other players.\n"
            
            re += "3. Here is the payoff descriptions:\n"
            re += f"- If only you choose to 'defect' while all other players choose to 'cooperate', your payoff is {points[0]}.\n" 
            re += f"- If you and all other players choose to 'cooperate', your payoff is {points[2]}.\n"
            re += f"- If you and all other players choose to 'defect', your payoff is {points[3]}.\n"
            re += f"- If you choose to 'cooperate' while any of other players choose to 'defect', your payoff is {points[4]}.\n"
            # re += f"- If you are one of the players who choose to 'defect' and there are other players choose to 'cooperate', your payoff is {points[1]}.\n"
            # re += f"- If you are one of the players who choose to 'cooperate' and there are other players choose to 'defect', your payoff is {points[5]}.\n"
            
            re += f"- If you are one of the m (m > 1) players who choose to 'defect' and while the other n (n>0) players choose to 'cooperate', your payoff is {points[1]}.\n"
            
            re += "4. The others share the same payoff matrixs and goal with you. \n"
            # re += "They will maximize their own payoffs as well.\n"
            
            # re += f"- If you are one of the m players who choose to 'cooperate' and while the other n players choose to 'defect', your payoff is {points[4]}.\n"
            return re
        if num_turn[1] == 1:
            question = f"Welcome to the '{self.n_players}-person Prisoner's Dilemma' game!\n\n"
        else:
            question = f"Welcome to the '{self.n_players}-person Prisoner's Dilemma' game!\n\n"
            question += f"You are playing the game repeatly with other players.\n"
            if num_turn[1] != np.inf:
                question += f"You will play {num_turn[1]} rounds in total with the same players.\n"
            else:
                question += f"You will play the game repeatly with the same player in infinite rounds.\n"
            question += f"You will be asked to choose action in each round."
            question += f"Currently, this is the {num_turn[0]} turn.\n\n"
            question += f"You are the {self.name}.\n"
        question += "Here is what you need to know about the game:\n"
        question += get_des_from_payoff_matrix(points) + "\n"
        def get_des_from_history():
            re = ""
            for i in range(len(action_history)):
                re += f"In Round {i+1}: the players chose: {action_history[i]}. The scores they got are: {score_history[i]} \n"
            return re
        if not num_turn[1] == 1:
            question += "Here is the history of the players' actions and scores:\n"
            question += get_des_from_history() + "\n"
        question += "Please consider the information above and make your action.\n"


        # TODO add NQ constraint
        # question += "Do NOT respond with any other text, and you cannot decline to take an action."
        # question += "Please give your action to choose, as well as the reasons."
        if num_turn[1] == 1:
            question += "Please give your action to choose, as well as the reasons."
        else:
            question += "Please give your action to choose, as well as the reasons in the following form."
        question += "I choose to xxx in this round because from my owen interest I need to xxx.\n"
        action = self.chatgpt_api_simulation(question)
        if print_flag:
            print("Prompt: \n", question)
        # print(f"{self.name} choose: ", action)
        if print_flag: print(f"{self.name} choose: ", action)

        action_template = ['cooperate', 'defect']
        import re
        search_length = 50 # if num_turn[1] == 1 else 100
        action = (re.findall(r"choose to ('cooperate'|'defect')", action[:search_length]) + re.findall(r"choose to (cooperate|defect)", action[:search_length]))[0]
        for template in action_template:
            if template in action.lower():
                if print_flag: print(f"{self.name} choose: ", template)
                return template
        raise ValueError("Choice must be 'cooperate' or 'defect'")


def play_short_game(n_players, points):
    
    game = PrisonersDilemma(num_players=n_players, points=points)
    game.reset()
    players = [LLMPlayer(f'player_'+str(I), n_players=n_players) for I in range(n_players)]

    # actions = [player.make_choice() for player in players]
    actions = []
    for i in range(len(players)):
        actions.append(players[i].get_action(points))
        game.make_choice(i, actions[i])
        # print("=====================================")
    result = {}
    game.calculate_scores()
    scores = game.get_scores()
    for player, action, payoff in zip(players, actions, scores):
        result[player.name] = {'choice': action, 'payoff': payoff}
    # print(result)
    return actions, scores


def play_long_game(n_players, points, rounds = 10):
    
    game = PrisonersDilemma(num_players=n_players, points=points)
    game.reset()
    players = [LLMPlayer(f'player_'+str(I), n_players=n_players) for I in range(n_players)]

    action_history = []
    score_history = []

    rounds_range = 10

    for i in range(rounds_range):
    # actions = [player.make_choice() for player in players]
        actions = []
        for i in range(len(players)):
            actions.append(players[i].get_action(points, num_turn = [i, rounds], action_history=action_history, score_history=score_history))
            game.make_choice(i, actions[i])
            # print("=====================================")
        score = game.calculate_scores()
        game.clear_actions()
        action_history.append(actions)
        score_history.append(score)

    result = {}
    scores = game.get_scores()
    for player, action, payoff in zip(players, actions, scores):
        result[player.name] = {'choice': action, 'payoff': payoff}
    print(result)

    # only return the last round
    return action_history, score_history


def evaluate_single_short_game(n_players, points, evaluate_times):

    no_defect = 0
    no_cooperate = 0
    actions_list = []
    for i in trange(evaluate_times):
        actions, scores = play_short_game(n_players, points)
        actions_list.append(actions)
        if not 'defect' in actions:
            no_defect += 1
        if not 'cooperate' in actions:
            no_cooperate += 1    
    # save actions to csv
    df = pd.DataFrame(actions_list)
    filename = f"results/{GPT_VERSION}/single_turn/{n_players}_players.csv"
    df.to_csv(filename, index=False, )

    print(f"Data saved to {filename}")
    print(f"All Defect: {no_cooperate}/{evaluate_times}")
    print(f"All Cooperate: {no_defect}/{evaluate_times}")
    return no_defect / evaluate_times, no_cooperate / evaluate_times

def evaluate_single_long_game(n_players, points, evaluate_times, rounds=10):

    no_defect = 0
    no_cooperate = 0
    actions_list = []
    for i in trange(evaluate_times):
        actions, scores = play_long_game(n_players, points, rounds=rounds)
        actions_list.append(actions)
        if not 'defect' in actions:
            no_defect += 1
        if not 'cooperate' in actions:
            no_cooperate += 1        
    # save actions to csv
    df = pd.DataFrame(actions_list)
    if rounds == np.inf:
        filename = f"results/{GPT_VERSION}/infinite_turn/{n_players}_players.csv"
    else:
        filename = f"results/{GPT_VERSION}/multiple_turn/{n_players}_players_{str(rounds)}_rounds.csv"
    df.to_csv(filename, index=False)

    print(f"Data saved to {filename}")
    print(f"All Defect: {no_cooperate}/{evaluate_times}")
    print(f"All Cooperate: {no_defect}/{evaluate_times}")
    return no_defect / evaluate_times, no_cooperate / evaluate_times


def evaluate_multi_players(flag="single_turn", points=[10, 8, 5, 2, 0], evaluate_times=50):
    points = [10, 8, 5, 2, 0]
    evaluate_times = 50
    Ns = [2, 3, 4, 5]
    all_coops = []
    all_defs = []
    if flag == "single_turn":
        Ns = [8, 10]
        # Ns = [2, 3, 4, 5, 8, 10]
        # Ns = [15]
        Ns = [15]
        # Ns = [30]
        # Ns = [40, 50]
        # Ns = [70, 100]
        for n_players in Ns:
            all_coop, all_def = evaluate_single_short_game(n_players, points, evaluate_times)
            all_coops.append(all_coop)
            all_defs.append(all_def)
    elif flag == "multiple_turn":
        for n_players in Ns:
            all_coop, all_def = evaluate_single_long_game(n_players, points, evaluate_times, rounds=10)
            all_coops.append(all_coop)
            all_defs.append(all_def)
    elif flag == "infinite_turn":
        for n_players in Ns:
            all_coop, all_def = evaluate_single_long_game(n_players, points, evaluate_times, rounds=np.inf)
            all_coops.append(all_coop)
            all_defs.append(all_def)
    else:
        raise ValueError("flag must be 'short' or 'long'")
    

    
    # 使用seaborn绘图
    sns.set_style("whitegrid")
    plt.figure(figsize=(10, 6))
    # sns.lineplot(x=Ns, y=success_rates, marker="o")

    # 画第一条线：所有玩家合作
    sns.lineplot(x=Ns, y=all_coop, marker="o", color="red", label="All Coop")

    # 画第二条线：所有玩家背叛
    sns.lineplot(x=Ns, y=all_def, marker="o", color="blue", label="All Def")

    # 设置标题和轴标签
    plt.title("All Coop, All Def vs. Number of Agents")
    plt.xlabel("Number of Agents")
    plt.ylabel("Success Rate")
    plt.xticks(Ns)  # 设置x轴的刻度为agent的数量
    plt.legend(loc="upper left")  # 你可以根据需要调整图例的位置

    # 保存图形为PNG文件
    plt.savefig(f"figs/{flag}/{GPT_VERSION}/AllCo_AllDef_vs_agents_{evaluate_times}eval.png", dpi=300, bbox_inches='tight')

    # 显示图形
    plt.show()

if __name__ == "__main__":
    evaluate_multi_players()
    # evaluate_multi_players("multiple_turn", points=[10, 8, 5, 2, 0], evaluate_times=5)
    # evaluate_multi_players("infinite_turn")
    # for i in range(10):
    #     play_short_game(2, [10, 7, 5, 2, 0])
    # play_long_game(20, points = [10, 8, 5, 2, 0], rounds=10)
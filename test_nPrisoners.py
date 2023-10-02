import argparse

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import trange

from games.prisoner_game import PrisonersDilemma
from player import LLMPlayer


def play_short_game(n_players, points, gpt_version):

    game = PrisonersDilemma(num_players=n_players, points=points)
    game.reset()
    players = [LLMPlayer(f'player_'+str(I), n_players=n_players, gpt_version=gpt_version)
               for I in range(n_players)]

    actions = []
    for i in range(len(players)):
        actions.append(players[i].get_action(points))
        game.make_choice(i, actions[i])
    result = {}
    game.calculate_scores()
    scores = game.get_scores()
    for player, action, payoff in zip(players, actions, scores):
        result[player.name] = {'choice': action, 'payoff': payoff}
    print(result)
    return actions, scores


def play_long_game(n_players, points, gpt_version, rounds=10):

    game = PrisonersDilemma(num_players=n_players, points=points)
    game.reset()
    players = [LLMPlayer(f'player_'+str(I), n_players=n_players, gpt_version=gpt_version)
               for I in range(n_players)]

    action_history = []
    score_history = []

    rounds_range = 10

    for r_i in range(rounds_range):
        actions = []
        for i in range(len(players)):
            actions.append(players[i].get_action(points, num_turn=[
                           r_i, rounds], action_history=action_history, score_history=score_history))
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

    return action_history, score_history


def evaluate_single_short_game(n_players, points, evaluate_times, gpt_version):

    no_defect = 0
    no_cooperate = 0
    actions_list = []
    for i in trange(evaluate_times):
        actions, scores = play_short_game(n_players, points, gpt_version)
        actions_list.append(actions)
        if not 'defect' in actions:
            no_defect += 1
        if not 'cooperate' in actions:
            no_cooperate += 1

    # save actions to csv
    df = pd.DataFrame(actions_list)
    filename = f"results/{gpt_version}/single_turn/{n_players}_players.csv"
    df.to_csv(filename, index=False, )

    print(f"Data saved to {filename}")
    print(f"All Defect: {no_cooperate}/{evaluate_times}")
    print(f"All Cooperate: {no_defect}/{evaluate_times}")
    return no_defect / evaluate_times, no_cooperate / evaluate_times


def evaluate_single_long_game(n_players, points, evaluate_times, gpt_version, rounds=10):

    no_defect = 0
    no_cooperate = 0
    actions_list = []
    for i in trange(evaluate_times):
        actions, scores = play_long_game(n_players, points, gpt_version, rounds=rounds)
        actions_list.append(actions)
        if not 'defect' in actions:
            no_defect += 1
        if not 'cooperate' in actions:
            no_cooperate += 1

    # save actions to csv
    df = pd.DataFrame(actions_list)
    if rounds == np.inf:
        filename = f"results/{gpt_version}/infinite_turn/{n_players}_players.csv"
    else:
        filename = f"results/{gpt_version}/multiple_turn/{n_players}_players_{str(rounds)}_rounds.csv"
    df.to_csv(filename, index=False)

    print(f"Data saved to {filename}")
    print(f"All Defect: {no_cooperate}/{evaluate_times}")
    print(f"All Cooperate: {no_defect}/{evaluate_times}")
    return no_defect / evaluate_times, no_cooperate / evaluate_times


def evaluate_multi_players(flag="single_turn", points=[10, 8, 5, 2, 0], evaluate_times=50, gpt_version='gpt-3.5-turbo'):
    all_coops = []
    all_defs = []
    points = [10, 8, 5, 2, 0]

    # To Configure
    if flag == "single_turn":
        Ns = [2, 3, 4, 5, 8, 10, 15, 20, 25, 30]
        for n_players in Ns:
            all_coop, all_def = evaluate_single_short_game(
                n_players, points, evaluate_times, gpt_version=gpt_version)
            all_coops.append(all_coop)
            all_defs.append(all_def)
    elif flag == "multiple_turn":
        Ns = [2, 3, 4, 5, 8, 10, 15, 20, 25, 30]
        for n_players in Ns:
            all_coop, all_def = evaluate_single_long_game(
                n_players, points, evaluate_times, gpt_version=gpt_version, rounds=10)
            all_coops.append(all_coop)
            all_defs.append(all_def)
    elif flag == "infinite_turn":
        Ns = [2, 3, 4, 5, 8, 10, 15]
        Ns = [15, 10, 8]
        for n_players in Ns:
            all_coop, all_def = evaluate_single_long_game(
                n_players, points, evaluate_times, gpt_version=gpt_version, rounds=np.inf)
            all_coops.append(all_coop)
            all_defs.append(all_def)
    else:
        raise ValueError("flag must be 'short' or 'long'")

    # draw by seaborn
    sns.set_style("whitegrid")
    plt.figure(figsize=(10, 6))

    # all cooperate
    sns.lineplot(x=Ns, y=all_coops, marker="o", color="red", label="All Coop")

    # all defect
    sns.lineplot(x=Ns, y=all_defs, marker="o", color="blue", label="All Def")

    # set figure
    plt.title("All Coop, All Def vs. Number of Agents")
    plt.xlabel("Number of Agents")
    plt.ylabel("Success Rate")
    plt.xticks(Ns) 
    plt.legend(loc="upper left") 

    plt.savefig(f"figs/{flag}/{gpt_version}/AllCo_AllDef_vs_agents_{evaluate_times}eval.png",
                dpi=300, bbox_inches='tight')

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MultiAgentHackathon')
    parser.add_argument('--gpt', default='gpt-3.5-turbo', type=str, help='version of chatgpt api')
    parser.add_argument('--num-eval', default='20', type=int, help='number of evalations')
    parser.add_argument('--repeated-game', default=False, action='store_true', help='if play repeated game')
    
    args = parser.parse_args()

    if args.repeated_game:
        evaluate_multi_players("infinite_turn", evaluate_times=args.num_eval, gpt_version=args.gpt)
    
    else:
        evaluate_multi_players(evaluate_times=args.num_eval, gpt_version=args.gpt)


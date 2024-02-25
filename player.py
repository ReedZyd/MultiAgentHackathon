import random
import openai
import time
import numpy as np

from utils import number_to_ordinal
import re

class Player:
    def __init__(self, name, n_players, actions=None):
        self.name = name
        if actions is None:
            actions = ['cooperate', 'defect']
        self.choices = actions
        self.n_players = n_players

    def get_action(self):
        return random.choice(self.choices)
class RandomPlayer(Player):
    def __init__(self, name, n_players, actions=None):
        super().__init__(name, n_players, actions)
    def get_action(self, points=None, num_turn=[1, 1], action_history=None, score_history=None, print_flag=True):
        return random.choice(self.choices)

class LLMJudge(Player):
    def __init__(self, name, n_players, gpt_version, actions=None):
        super().__init__(name, n_players, actions)
        self.gpt_version = gpt_version

    def chatgpt_api_simulation(self, prompt, stop=["\n"]):
        i = 2
        while True:
            try:
                # time.sleep(1)
                completion = openai.ChatCompletion.create(
                    model=self.gpt_version,
                    messages=[
                        {"role": "system", "content": "You are a player involved in the 'Prisoner's Dilemma' game.\n\n"},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                    top_p=0.5,
                )
                return completion.choices[0].message['content']
            except:
                i = i * 2
                print("Error in LLM, sleep seconds: ", i)
                time.sleep(i)
                if i > 128:
                    return {'content': ''}
                
    def get_action(self, points=None, num_turn=[1, 1], action_history=None, score_history=None, print_flag=True):
        question = f"Welcome to the '{self.n_players}-person Prisoner's Dilemma' game!\n\n"
        if not num_turn[1] == 1:
            question = f"Welcome to the '{self.n_players}-person Prisoner's Dilemma' game!\n\n"
            if num_turn[1] != np.inf:
                question += f"You are playing {num_turn[1]} rounds in total with the same players.\n"
            else:
                question += f"You are playing the game repeatly with the same player in infinite rounds.\n"
            #TODO:'promote cooperative behavior'/'maximize the team reward'
            question += f"Your goal is to promote cooperative behavior among agents by allocating different rewards to different agents, 
                            with the total value of the allocated rewards not exceeding a fixed amount." 
            #TODO:a fixed amount should be the current sum of the scores of all agents
            question += f"You will be asked to decide how much reward to allocate to each agent. "
            # question += f"Currently, this is the {number_to_ordinal(num_turn[0])} turn.\n\n"
            question += f"You are the {self.name}.\n"

        question += "Here is what you need to know about the game:\n"
        question += self.get_des_from_payoff_matrix(points, num_turn, self.n_players) + "\n"

        if not num_turn[1] == 1:
            question += self.get_des_from_history(action_history, score_history) + "\n"
        question += "Please consider the information above and make your action.\n"
        if num_turn[1] == 1:
            question += "Please give your allocation method, as well as the reasons."
        else:
            question += "Please give your allocation method, as well as the reasons in the following form."

        question += "I choose to xxx in this round because from my own interest I need to xxx.\n"
        
        # get action
        action = self.chatgpt_api_simulation(question)
        if print_flag:
            print("Prompt: \n", question)
            print(f"{self.name} choose: ", action)

        search_length = 50 if num_turn[1] == 1 else 100
        # action = (re.findall(r"choose to ('cooperate'|'defect')", action[:search_length]) + re.findall(
        #     r"choose to (cooperate|defect)", action[:search_length]))[0]
        action = (re.findall(r"choose to ('cooperate'|'defect')", action[:search_length]) + re.findall(
            r"choose to (cooperate|defect)", action[:search_length]))[0] #TODO: notsure how to alter here
        print(self.choices)

        for template in self.choices:
            if template in action.lower():
                if print_flag:
                    print(f"{self.name} choose: ", template)
                return template
            
        raise ValueError("Choice must be 'cooperate' or 'defect'")
    
    def get_des_from_history(self, action_history, score_history):
        re = ""
        for i in range(len(action_history)):
            if i == 0:
                re += "Here is the history of the players' actions and scores:\n"
            re += f"In Round {i+1}: the players chose: {action_history[i]}. The scores they got are: {score_history[i]} \n"
        return re
    
    def get_des_from_payoff_matrix(self, points, num_turn,n_players):
        re = "1. As a judge, your reward allocation method should be like [0] * {n_players}.\n" #TODO: dont know if that's correct
        if num_turn[1] == 1:
            re += "2. Remember your goal is to maximize the total payoff. "
        else:
            re += "2. Remember your goal is to maximize the total accumulative discounted payoff. "
            re += "The discounted factor is 0.9. \n"
        re += "3. You should only care about the total payoff.\n"

        re += "4. Here are the payoff descriptions:\n"
        if n_players == 2:
            re += f"- If the first agent choose to 'defect' and the second agent choose to 'defect', the first agent's payoff is {points[1]}, the second agent's payoff is {points[1]}.\n"
            re += f"- If the first agent choose to 'defect' and the second agent choose to 'cooperate', the first agent's payoff is {points[3]}, the second agent's payoff is {points[0]}.\n"
            re += f"- If the first agent choose to 'cooperate' and the second agent choose to 'defect', the first agent's payoff is {points[0]}, the second agent's payoff is {points[3]}.\n"
            re += f"- If the first agent choose to 'cooperate' and the second agent choose to 'cooperate', the first agent's payoff is {points[2]}, the second agent's payoff is {points[2]}.\n"
        elif n_players == 3:
            re += f"- If the first agent choose to 'defect' and the second agent choose to 'defect' and the third agent choose to 'defect', the first agent's payoff is {points[1]}, the second agent's payoff is {points[1]}, the third agent's payoff is {points[1]}.\n"
            re += f"- If the first agent choose to 'defect' and the second agent choose to 'defect' and the third agent choose to 'cooperate', the first agent's payoff is {points[3]}, the second agent's payoff is {points[3]}, the third agent's payoff is {points[0]}.\n"
            re += f"- If the first agent choose to 'defect' and the second agent choose to 'cooperate' and the third agent choose to 'defect', the first agent's payoff is {points[3]}, the second agent's payoff is {points[0]}, the third agent's payoff is {points[3]}.\n"
            re += f"- If the first agent choose to 'defect' and the second agent choose to 'cooperate' and the third agent choose to 'cooperate', the first agent's payoff is {points[5]}, the second agent's payoff is {points[2]}, the third agent's payoff is {points[2]}.\n"
            re += f"- If the first agent choose to 'cooperate' and the second agent choose to 'defect' and the third agent choose to 'defect', the first agent's payoff is {points[0]}, the second agent's payoff is {points[3]}, the third agent's payoff is {points[3]}.\n"
            re += f"- If the first agent choose to 'cooperate' and the second agent choose to 'defect' and the third agent choose to 'cooperate', the first agent's payoff is {points[2]}, the second agent's payoff is {points[5]}, the third agent's payoff is {points[2]}.\n"
            re += f"- If the first agent choose to 'cooperate' and the second agent choose to 'cooperate' and the third agent choose to 'defect', the first agent's payoff is {points[2]}, the second agent's payoff is {points[2]}, the third agent's payoff is {points[5]}.\n"
            re += f"- If the first agent choose to 'cooperate' and the second agent choose to 'cooperate' and the third agent choose to 'cooperate', the first agent's payoff is {points[4]}, the second agent's payoff is {points[4]}, the third agent's payoff is {points[4]}.\n"


        # re += "5. The others share the same payoff matrix and goal with you. \n"
        return re

class LLMPlayer(Player):
    def __init__(self, name, n_players, gpt_version, actions=None):
        super().__init__(name, n_players, actions)
        self.gpt_version = gpt_version
    def chatgpt_api_simulation(self, prompt, stop=["\n"]):
        i = 2
        while True:
            try:
                # time.sleep(1)
                completion = openai.ChatCompletion.create(
                    model=self.gpt_version,
                    messages=[
                        {"role": "system", "content": "You are a player involved in the 'Prisoner's Dilemma' game.\n\n"},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                    top_p=0.5,
                )
                return completion.choices[0].message['content']
            except:
                i = i * 2
                print("Error in LLM, sleep seconds: ", i)
                time.sleep(i)
                if i > 128:
                    return {'content': ''}

    def get_action(self, points=None, num_turn=[1, 1], action_history=None, score_history=None, print_flag=True):

        question = f"Welcome to the '{self.n_players}-person Prisoner's Dilemma' game!\n\n"
        if not num_turn[1] == 1:
            question = f"Welcome to the '{self.n_players}-person Prisoner's Dilemma' game!\n\n"
            if num_turn[1] != np.inf:
                question += f"You are playing {num_turn[1]} rounds in total with the same players.\n"
            else:
                question += f"You are playing the game repeatly with the same player in infinite rounds.\n"
                
            question += f"You will be asked to choose action in each round. "
            question += f"Currently, this is the {number_to_ordinal(num_turn[0])} turn.\n\n"
            question += f"You are the {self.name}.\n"

        question += "Here is what you need to know about the game:\n"
        question += self.get_des_from_payoff_matrix(points, num_turn) + "\n"


        if not num_turn[1] == 1:
            question += self.get_des_from_history(action_history, score_history) + "\n"
        question += "Please consider the information above and make your action.\n"
        if num_turn[1] == 1:
            question += "Please give your action to choose, as well as the reasons."
        else:
            question += "Please give your action to choose, as well as the reasons in the following form."

        question += "I choose to xxx in this round because from my own interest I need to xxx.\n"
        
        # get action
        action = self.chatgpt_api_simulation(question)
        if print_flag:
            print("Prompt: \n", question)
            print(f"{self.name} choose: ", action)

        search_length = 50 if num_turn[1] == 1 else 100
        action = (re.findall(r"choose to ('cooperate'|'defect')", action[:search_length]) + re.findall(
            r"choose to (cooperate|defect)", action[:search_length]))[0]
        print(self.choices)

        for template in self.choices:
            if template in action.lower():
                if print_flag:
                    print(f"{self.name} choose: ", template)
                return template
            
        raise ValueError("Choice must be 'cooperate' or 'defect'")
    

    def get_des_from_history(self, action_history, score_history):
        re = ""
        for i in range(len(action_history)):
            if i == 0:
                re += "Here is the history of the players' actions and scores:\n"
            re += f"In Round {i+1}: the players chose: {action_history[i]}. The scores they got are: {score_history[i]} \n"
        return re
    def get_des_from_payoff_matrix(self, points, num_turn):
        re = "1. As a player, you can choose from: 'cooperate', 'defect'.\n"
        if num_turn[1] == 1:
            re += "2. Remember your goal is to maximize your own payoff. "
        else:
            re += "2. Remember your goal is to maximize your own accumulative discounted payoff. "
            re += "The discounted factor is 0.9. \n"
        re += "3. You should only care about your own interests.\n"

        re += "4. Here are the payoff descriptions:\n"
        re += f"- If only you choose to 'defect' while all other players choose to 'cooperate', your payoff is {points[0]}.\n"
        re += f"- If you and all other players choose to 'cooperate', your payoff is {points[2]}.\n"
        re += f"- If you and all other players choose to 'defect', your payoff is {points[3]}.\n"
        re += f"- If you choose to 'cooperate' while any of other players choose to 'defect', your payoff is {points[4]}.\n"
        re += f"- If you are one of the m (m > 1) players who choose to 'defect' and while the other n (n>0) players choose to 'cooperate', your payoff is {points[1]}.\n"

        re += "5. The others share the same payoff matrix and goal with you. \n"
        return re
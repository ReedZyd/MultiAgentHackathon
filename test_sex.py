
from sex_game import BattleOfSexes3
from player import Player
import openai
import time

class LLMPlayer(Player):

    def chatgpt_api_simulation(self, prompt, stop=["\n"]):
        # 这是一个模拟的API函数，它返回一个随机选择。
        # 在真实的实现中，这里应该是与ChatGPT的真实交互。
        i = 2
        while True:
            try:
                time.sleep(1)
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    # model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a player involved in the 'Battle of Sexs' game.\n\n"},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.5,
                    top_p=0.5,
                )
                print(completion.choices[0])
                return completion.choices[0].message['content']
            except:
                # num_tokens = num_tokens(prompt)

                i = i * 2
                print("Error in LLM, sleep seconds: ", i)
                time.sleep(i)
                if i > 32:
                    return {'content': ''}


    def get_action(self, payoff_matrix=None):
        def get_des_from_payoff_matrix(payoff_matrix):
            des = ""
            for key, value in payoff_matrix.items():
                des += f"If the three player choices: {key}, separately -> The three players will get: {value}, separately.\n"
            des += "Otherwise, all of you get 0.\n"
            return des
        # question = f"You are playing the 'Battle of Sexs' game now. Here are three players in the game. You are the {self.name}\n"
        question = f"Here are three players in the 'Battle of Sexs' game. You are the {self.name}.\n"
        question += "Given the payoff matrix, what should you choose?\n"
        question += "Here is the payoff descriptions:\n"
        question += get_des_from_payoff_matrix(payoff_matrix) + "\n"
        question += "Please choose one of the following actions: " + str(self.choices) + "\n"
        question += "Do NOT respond with any other text, and you cannot decline to take an action."
        action = self.chatgpt_api_simulation(question)
        print("Prompt: \n", question)
        print(f"{self.name} choose: ", action)
        return action
    
n_players = 3
game = BattleOfSexes3()
actions = game.get_actions()

players = [LLMPlayer(f'player_'+str(I), n_players=n_players, actions = actions) for I in range(3)]

# actions = [player.make_choice() for player in players]
actions = []
for i in range(len(players)):
    actions.append(players[i].make_choice(payoff_matrix=game.payoff_matrix))
    print("=====================================")
result = {}
payoffs = game.get_payoff(tuple(actions))
for player, action, payoff in zip(players, actions, payoffs):
    result[player.name] = {'choice': action, 'payoff': payoff}

print(result)


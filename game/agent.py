import random

class GameAgent:
    def choose_action(self, current_state):
        raise NotImplementedException("You must implement the choose_action method in a subclass of GameAgent!")


class RandomGameAgent(GameAgent):
    def choose_action(self, current_state):
        actions = current_state.actions()
        chosen_action = random.choice(actions)
        return chosen_action


class GreedyGameAgent(GameAgent):
    def choose_action(self, current_state):
        actions = current_state.actions()
        max_reward = -1
        best_action = None
        for action in actions:
            piles, next_state, reward = action
            if reward > max_reward:
                max_reward = reward
                best_action = action

        return best_action

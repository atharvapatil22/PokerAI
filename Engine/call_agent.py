from player import Player
from player import Action
from agent import Agent

class CallAgent(Agent):

    def get_action(self, board, validActions):
        action = None
        if Action.CALL in validActions:
            action = Action.CALL
        else:
            action = Action.CHECK
        return action
from player import Player
from player import Action
from agent import Agent

class CallAgent(Agent):

    def get_action(self, board, validActions):
        action = None
        if Action.CALL in validActions:
            action = Action.CALL
        elif Action.CHECK in validActions:
            action = Action.CHECK
        else :
            action = Action.ALL_IN
        return action
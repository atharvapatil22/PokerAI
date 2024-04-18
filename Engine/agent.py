from player import Player
from player import Action
from abc import ABC, abstractmethod

class Agent(Player):

    @abstractmethod
    def get_action(self, board, validActions):
        pass  
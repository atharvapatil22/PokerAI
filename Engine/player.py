from enum import Enum
from abc import ABC, abstractmethod

class Action(Enum):
    MIN_BET = "min_bet"
    LOW_BET = "low_bet"
    MID_BET = "mid_bet"
    HIGH_BET = "high_bet"
    ALL_IN = "all_in"
    CALL = "call"
    CHECK = "check"
    FOLD = "fold"

class Player(ABC):

    def __init__(self, id, chips):
        self.cardsInHand = [] # Will be cleared by round after every round
        self.id = id
        self.chips = chips
        self.current_bet = 0 # Will be cleared by round after every round

    # Will be implemented accordingly depending on the type of agent or a real player
    @abstractmethod 
    def get_action(self, board, validActions):
        pass
   
    # Will be called by round in order to give the player cards
    def deal(self, card):
        self.cardsInHand.append(card)

    # Will be called when the player bets
    def bet(self, amount):
        self.chips -= amount
        self.bet += amount

    # Will be called by round when the player wins a betting round
    def win_round(self, pot):
        self.chips += pot

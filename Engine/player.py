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
    OP_MAX = "op_max" # Short for "Opponent_Max"

class Player(ABC):

    def __init__(self, id, chips):
        self.cardsInHand = [] # Will be cleared by round after every round
        self.id = id
        self.chips = chips
        self.current_bet = 0 # Will be cleared by round after every round

        # Is used to store the number of chips this player has at the end of every round of every game the player plays
        # It will be a 2D array, the first index gets you into a game, the next gives you the chips the player had at
        # the end of that round of the chosen game.
        self.chipRecord = [] # Will NOT be cleared on end of round or game
        self.gameidx = -1 # Will NOT be cleared on end of round or game, is incremented at the start of each game

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
        self.current_bet += amount
        return amount

    # Will be called by round when the player wins a betting round
    def win_round(self, pot):
        self.chips += pot

    # Will be called by round at the end of the round
    def recordChips(self):
        self.chipRecord[self.gameidx].append(self.chips)
    
    # Will be called by poker at the start of the game
    def nextGame(self):
        self.gameidx += 1
        self.chipRecord.append([])
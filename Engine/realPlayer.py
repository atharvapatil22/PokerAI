from player import Player
from player import Action

class RealPlayer(Player):

    def get_action(self, board):
        print(f"The pot is: {board.pot}.")
        print(f"The community cards are: {board.community}.")
        print(f"Your hand is: {self.cardsInHand}.")
        print(f"You have {self.chips} chips left.")
        print(f"You have bet {self.current_bet}.")
        print(f"The current bet is {board.currentBet}.")
        incomingBet = board.currentBet - self.current_bet
        print(f"The incoming bet is {incomingBet}.")
        # LOW_BET = 10%
        # MID_BET = 40%
        # HGH_BET = 70%
        # ALL_IN  = 100%
        # CALL = CHECK = Up to current bet
        # FOLD = drop out
        print(f'''
            Your options are:
            MIN_BET ({incomingBet} + {board.minBet} = {incomingBet + board.minBet}) (raise)
            LOW_BET ({incomingBet} + {self.chips * 0.1 if self.chips * 0.1 > self.minBet else self.minBet} = {incomingBet + self.chips * 0.1 if self.chips * 0.1 > self.minBet else self.minBet}) (raise)
            MID_BET ({incomingBet} + {self.chips * 0.4 if self.chips * 0.4 > self.minBet else self.minBet} = {incomingBet + self.chips * 0.4 if self.chips * 0.4 > self.minBet else self.minBet}) (raise)
            HGH_BET ({incomingBet} + {self.chips * 0.7 if self.chips * 0.7 > self.minBet else self.minBet} = {incomingBet + self.chips * 0.7 if self.chips * 0.7 > self.minBet else self.minBet}) (raise)
            ALL_IN  ({self.chips})
            CALL ({incomingBet}) (cannot perform when the incoming bet is 0)
            CHECK (only if incoming bet is 0 and no players have bet or raised before you)
            FOLD (drop out)
            ''')
        # Request player action
        action = None
        while action == None:
            action = input("What would you like to do? ").upper()
            action = action.upper()
            action = self.validate_input(action, board)
        return action
    
    def parse_input(self, action):
        if action == "MIN_BET":
            return Action.MIN_BET
        elif action == "LOW_BET":
            return Action.LOW_BET
        elif action == "MID_BET":
            return Action.MID_BET
        elif action == "HIGH_BET":
            return Action.HIGH_BET
        elif action == "ALL_IN":
            return Action.ALL_IN
        elif action == "CALL":
            return Action.CALL
        elif action == "CHECK":
            return Action.CHECK
        elif action == "FOLD":
            return Action.FOLD
        else:
            print("Invalid input. Try again.")
            return None
    
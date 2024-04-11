from player import Player
from player import Action

class RealPlayer(Player):

    def get_action(self, board, validActions):
        print(f"The pot is: {board.pot}.")
        print("The community cards are: " + ", ".join(str(card) for card in board.community))
        print("Your hand is: " + ", ".join(str(card) for card in self.cardsInHand))
        print(f"You have {self.chips} chips left.")
        print(f"You have bet {self.current_bet}.")
        print(f"The current bet is {board.currentBet}.")
        incomingBet = board.currentBet - self.current_bet
        print(f"The incoming bet is {incomingBet}.")
        # LOW_BET = 10%
        # MID_BET = 40%
        # HIGH_BET = 70%
        # ALL_IN  = 100%
        # CALL = CHECK = Up to current bet
        # FOLD = drop out
        MIN_BET_STR = "" if Action.MIN_BET not in validActions else f"MIN_BET ({incomingBet} + {board.minBet} = {incomingBet + board.minBet}) (raise)\n"
        LOW_BET_STR = "" if Action.LOW_BET not in validActions else f"LOW_BET ({incomingBet} + {self.chips * 0.1 if self.chips * 0.1 > board.minBet else board.minBet} = {incomingBet + self.chips * 0.1 if self.chips * 0.1 > board.minBet else board.minBet}) (raise)\n"
        MID_BET_STR = "" if Action.MID_BET not in validActions else f"MID_BET ({incomingBet} + {self.chips * 0.4 if self.chips * 0.4 > board.minBet else board.minBet} = {incomingBet + self.chips * 0.4 if self.chips * 0.4 > board.minBet else board.minBet}) (raise)\n"
        HIGH_BET_STR = "" if Action.HIGH_BET not in validActions else f"HIGH_BET ({incomingBet} + {self.chips * 0.7 if self.chips * 0.7 > board.minBet else board.minBet} = {incomingBet + self.chips * 0.7 if self.chips * 0.7 > board.minBet else board.minBet}) (raise)\n"
        ALL_IN_STR = "" if Action.ALL_IN not in validActions else f"ALL_IN  ({self.chips})\n"
        CALL_STR = "" if Action.CALL not in validActions else f"CALL ({incomingBet}) (cannot perform when the incoming bet is 0)\n"
        CHECK_STR = "" if Action.CHECK not in validActions else f"CHECK (only if incoming bet is 0 and no players have bet or raised before you)\n"
        FOLD_STR = "" if Action.FOLD not in validActions else f"FOLD (drop out)\n"
        print(f'''
            Your options are:
            {MIN_BET_STR}
            {LOW_BET_STR}
            {MID_BET_STR}
            {HIGH_BET_STR}
            {ALL_IN_STR}
            {CALL_STR}
            {CHECK_STR}
            {FOLD_STR}
            ''')
        # Request player action
        action = None
        while action == None:
            action = input("What would you like to do? ").upper()
            action = action.upper()
            action = self.validate_input(action, validActions)
        return action
    
    def validate_input(self, action, validActions):
        action_enum = None
        if action == "MIN_BET":
            action_enum = Action.MIN_BET
        elif action == "LOW_BET":
            action_enum = Action.LOW_BET
        elif action == "MID_BET":
            action_enum = Action.MID_BET
        elif action == "HIGH_BET":
            action_enum = Action.HIGH_BET
        elif action == "ALL_IN":
            action_enum = Action.ALL_IN
        elif action == "CALL":
            action_enum = Action.CALL
        elif action == "CHECK":
            action_enum = Action.CHECK
        elif action == "FOLD":
            action_enum = Action.FOLD
        if action_enum not in validActions or action_enum == None:
            print("Invalid action. Try again.")
            return None
        return action_enum
    
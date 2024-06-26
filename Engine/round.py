from realPlayer import RealPlayer
from deck import Deck
from player import Action, BetRatio

class Round:
    class Board:
        def __init__(self,players,minBet,buttonPlayerIndex):
            self.pot = 0
            self.community = []
            self.playersPassing = []
            self.playersFolding = []
            self.playersAllIn = []
            self.playerBets = []
            self.currentBet = 0
            self.activePlayerIndex = 0
            self.minBet = minBet

            # NOTE: This extra state here is used to give the agents access to player chip balances
            #       This is risky, as it relies on consisent shallow copies to maintain data integrity,
            #       but in theory it should give us the info we need
            self.players = players
            # NOTE: This extra state here is used to give the agents access to button position
            #       It's used to allow the agents to know how to pass the button on simulation
            self.buttonPlayerIndex = buttonPlayerIndex

            # NOTE: This extra state here could have redundancy removed by forcing round methods to rely on it
            #       Instead of the existing round state.
            # Extra state redundant to round, included here so that agents can see it
            self.phase = 1
            self.checkFlag = True
            
            # Setup state arraylists
            for i in range(players.__len__()):
                self.playersPassing.append(False)
                self.playersAllIn.append(False)
                self.playerBets.append(0)
            # Handle the blinds
            self.currentBet = minBet



    def __init__(self, players, deck, minBet, buttonPlayerIndex = 0, supressOutput=False):
        self.players = players
        self.deck = deck
        self.minBet = minBet
        self.buttonPlayerIndex = buttonPlayerIndex
        self.board = self.Board(players,self.minBet,buttonPlayerIndex)
        self.checkFlag = True
        self.supressOuptut = supressOutput

    # Function will determine all the valid actions for the active player
    def getValidPlayerActions(self,incomingBet, activePlayerIndex):
        # Copy all the player actions
        validActions = [member for _, member in Action.__members__.items()]
        if not self.supressOuptut:
            print("player index",activePlayerIndex)
            print("player ID", self.players[activePlayerIndex].id)
        if self.checkFlag and incomingBet == 0:
            # CANNOT CALL -> phase bet is 0
            validActions.remove(Action.CALL)
        elif incomingBet >= self.players[int(activePlayerIndex)].chips:
            # CANNOT CALL -> Not enough chips
            validActions.remove(Action.CALL)
        if (not self.checkFlag) or incomingBet != 0:
            # CANNOT CHECK -> You must call, raise, or fold
            validActions.remove(Action.CHECK)
        if incomingBet + self.minBet > self.players[int(activePlayerIndex)].chips:
            # Not enough chips
            validActions.remove(Action.MIN_BET)
            validActions.remove(Action.LOW_BET)
            validActions.remove(Action.MID_BET)
            validActions.remove(Action.HIGH_BET)
        # OP_MAX action handling
        opponentIdx = (activePlayerIndex + 1) % self.players.__len__()
        if self.players[int(opponentIdx)].chips == 0:
            # Opponent is already all in
            validActions.remove(Action.OP_MAX)
            if Action.MIN_BET in validActions:
                validActions.remove(Action.MIN_BET)
            if Action.MID_BET in validActions:
                validActions.remove(Action.MID_BET)
            if Action.HIGH_BET in validActions:
                validActions.remove(Action.HIGH_BET)
        if self.players[int(opponentIdx)].chips + incomingBet >= self.players[int(activePlayerIndex)].chips:
            # Not enough chips to overbet other player
            if Action.OP_MAX in validActions:
                validActions.remove(Action.OP_MAX)
        else:
            # These actions would now overbet the opponent max
            validActions.remove(Action.ALL_IN)
            opponentMax = self.players[int(opponentIdx)].chips
            if incomingBet + self.players[activePlayerIndex].chips * BetRatio.LOW_BET > opponentMax:
                if Action.LOW_BET in validActions:
                    validActions.remove(Action.LOW_BET)
            if incomingBet + self.players[activePlayerIndex].chips * BetRatio.MID_BET > opponentMax:
                if Action.MID_BET in validActions:
                    validActions.remove(Action.MID_BET)
            if incomingBet + self.players[activePlayerIndex].chips * BetRatio.HIGH_BET > opponentMax:
                if Action.HIGH_BET in validActions:
                    validActions.remove(Action.HIGH_BET)
        
        return validActions

    # handle functionality when active player places MIN/LOW/MID/HIGH bet 
    def handleBet(self,action,activePlayerIndex,incomingBet):
        # Calculate player bet
        if action == Action.MIN_BET:
            playerBet = incomingBet + self.minBet
        elif action == Action.LOW_BET:
            playerBet = incomingBet + self.players[activePlayerIndex].chips * BetRatio.LOW_BET if self.players[activePlayerIndex].chips * BetRatio.LOW_BET > self.minBet else self.minBet
        elif action == Action.MID_BET:
            playerBet = incomingBet + self.players[activePlayerIndex].chips * BetRatio.MID_BET if self.players[activePlayerIndex].chips * BetRatio.MID_BET > self.minBet else self.minBet
        elif action == Action.HIGH_BET:
            playerBet = incomingBet + self.players[activePlayerIndex].chips * BetRatio.HIGH_BET if self.players[activePlayerIndex].chips * BetRatio.HIGH_BET > self.minBet else self.minBet

        # Update the stored player bet thus far
        self.board.playerBets[activePlayerIndex] += playerBet

        # Update the current bet
        self.board.currentBet = self.board.playerBets[activePlayerIndex]

        # Player is passing
        self.board.playersPassing[activePlayerIndex] = True
        # Other players must respond to the bet
        for i in range(self.board.playersPassing.__len__()):
            if i == activePlayerIndex:
                continue
            elif self.board.playersAllIn[i]:
                continue
            self.board.playersPassing[i] = False
        
        # print(f"Players passing(IN BET): {self.board.playersPassing}")

        # Update the pot
        self.board.pot += self.players[activePlayerIndex].bet(playerBet)

        # Disable checking if enabled
        if self.checkFlag:
            self.checkFlag = False
            self.board.checkFlag = False
            # Not needed after the Phase Change Logic Fix
            # for i in range(self.board.playersPassing.__len__()):
            #     self.board.playersPassing[i] = False
        
    # handle functionality when active player goes all in
    def handleAllIn(self,activePlayerIndex):
        # Calculate player bet
        playerBet = self.players[activePlayerIndex].chips

        # Update the stored player bet thus far
        self.board.playerBets[activePlayerIndex] += playerBet

        # Prompt response from other players if the ALL_IN raises the current bet
        promptResponse = False

        # Update the current bet
        if self.board.playerBets[activePlayerIndex] > self.board.currentBet:
            self.board.currentBet = self.board.playerBets[activePlayerIndex]
            promptResponse = True

        # Old logic:
        # # Passing if they have 0 chips remaining (have already all-inned)
        # self.board.playersPassing[activePlayerIndex] = False if self.players[activePlayerIndex].chips > 0 else True

        # Player is passing
        self.board.playersPassing[activePlayerIndex] = True
        # If 
        if promptResponse:
            # Disable checking if enabled
            if self.checkFlag:
                self.checkFlag = False
                self.board.checkFlag = False
            # Other players must respond to the bet
            for i in range(self.board.playersPassing.__len__()):
                if i == activePlayerIndex:
                    continue
                elif self.board.playersAllIn[i]:
                    continue
                self.board.playersPassing[i] = False

        # Update the pot
        self.board.pot += self.players[activePlayerIndex].bet(playerBet)

        # Disable checking if enabled
        # if self.checkFlag:
        #     self.checkFlag = False
        #     self.board.checkFlag = False
            # Not needed after the Phase Change Logic Fix
            # for i in range(self.board.playersPassing.__len__()):
            #     self.board.playersPassing[i] = False

        self.board.playersAllIn[activePlayerIndex] = True

    # handle functionality when active player bets opponent max
    def handleOpMax(self,activePlayerIndex,incomingBet):
        # Calculate player bet
        opponentMax = self.players[int((activePlayerIndex + 1) % self.players.__len__())].chips
        playerBet = incomingBet + opponentMax

        # Update the stored player bet thus far
        self.board.playerBets[activePlayerIndex] += playerBet

        # Player is passing
        self.board.playersPassing[activePlayerIndex] = True
        # Other players must respond to the bet
        for i in range(self.board.playersPassing.__len__()):
            if i == activePlayerIndex:
                continue
            elif self.board.playersAllIn[i]:
                continue
            self.board.playersPassing[i] = False

        # Update the current bet
        if self.board.playerBets[activePlayerIndex] > self.board.currentBet:
            self.board.currentBet = self.board.playerBets[activePlayerIndex]

        # Update the pot
        self.board.pot += self.players[activePlayerIndex].bet(playerBet)

        # Disable checking if enabled
        if self.checkFlag:
            self.checkFlag = False
            self.board.checkFlag = False
            # Not needed after the Phase Change Logic Fix
            # for i in range(self.board.playersPassing.__len__()):
            #     self.board.playersPassing[i] = False

        # While not technically "all in", in a two player game, this is sufficient tracking
        self.board.playersAllIn[activePlayerIndex] = True

    # handle functionality when active player calls
    def handleCall(self,activePlayerIndex,incomingBet):
        # Calculate player bet
        playerBet = incomingBet
        # Update the stored player bet thus far
        self.board.playerBets[activePlayerIndex] += playerBet
        # Player is Passing
        self.board.playersPassing[activePlayerIndex] = True
        # Update the pot
        self.board.pot += self.players[activePlayerIndex].bet(playerBet)

     # Returns the score of the best hand a player can make.
    def handScore(self,activePlayerIndex):
        # Consolidate cards
        cards = self.players[activePlayerIndex].cardsInHand + self.board.community

        SUITS = ["Spades", "Clubs", "Diamonds", "Hearts"]
        
        # Create vals and suits arrays for easier parsing and scoring
        vals = []
        suits = []
        for card in cards:
            vals.append(card.value)
            suits.append(card.suit)
        vals.sort()

        # Note High Card
        HIGH_CARD = vals[-1]

        
        


        # Check for Flush
        # Initialize variables
        # Marker
        FLUSH = False
        # NOT NEEDED REMOVE SOON
        FLUSH_HIGH = 0
        # Suit of the flush, stored for use in straight flush detection
        FLUSH_SUIT = ""
        # Set of the flush cards, used for finding the highest 5 cards in the flush
        flushSet = []
        # For each suit
        for suit in SUITS:
            # If there are 5 or more of that suit
            if suits.count(suit) >=5:
                # Update variables
                FLUSH = True
                FLUSH_SUIT = suit
                # Add the variables to the flush set
                for card in cards:
                    if card.suit == suit and card.value > FLUSH_HIGH:
                        FLUSH_HIGH = card.value
                    if card.suit == suit:
                        flushSet.append(card.value)
                break
        # Reverse sort the flush set for scoring convenience
        flushSet.sort(reverse=True)

            
        # Check for 4 of a kind
        FOUR_KIND = False
        FOUR_KIND_VAL = 0
        # Check for 3 of a kind
        THREE_KIND = False
        THREE_KIND_VAL = 0
        THREE_KIND_SECONDARY = 0
        # Check for 2 of a kind
        TWO_KIND = False
        TWO_KIND_VAL = 0
        # Check for 2 pairs
        TWO_PAIRS = False
        TWO_PAIRS_HIGH = 0
        # val takes on values 2 through 14 (2 through Ace)
        for i in range(13):
            val = i + 2
            if vals.count(val) == 4:
                FOUR_KIND = True
                FOUR_KIND_VAL = val
            elif vals.count(val) == 3:
                if THREE_KIND == True:
                    THREE_KIND_SECONDARY = THREE_KIND_VAL
                    THREE_KIND_VAL = val
                else:
                    THREE_KIND = True
                    THREE_KIND_VAL = val
            elif vals.count(val) == 2:
                # If two pairs have already been detected, shift the values down
                if TWO_PAIRS:
                    # Two kind val becomes the old two pairs high val
                    TWO_KIND_VAL = TWO_PAIRS_HIGH
                    # Two pairs high val becomes the current value
                    TWO_PAIRS_HIGH = val
                # If only one pair has already been detected, store the current value in the two pairs high val
                elif TWO_KIND:
                    TWO_PAIRS = True
                    TWO_PAIRS_HIGH = val
                # Otherwise, update two kind val
                else:
                    TWO_KIND = True
                    TWO_KIND_VAL = val
        
    
        # Check for Full house
        # Marker
        FULL_HOUSE = False
        # Value of the triple
        FULL_HOUSE_HIGH = 0
        # Value of the double
        FULL_HOUSE_LOW = 0
        # Take the highest value pair as your double if there are two
        if THREE_KIND and TWO_PAIRS:
            FULL_HOUSE = True
            FULL_HOUSE_HIGH = THREE_KIND_VAL
            FULL_HOUSE_LOW = TWO_PAIRS_HIGH
        elif THREE_KIND and TWO_KIND:
            FULL_HOUSE = True
            FULL_HOUSE_HIGH = THREE_KIND_VAL
            FULL_HOUSE_LOW = TWO_KIND_VAL
        elif THREE_KIND and THREE_KIND_SECONDARY != 0:
            FULL_HOUSE = True
            FULL_HOUSE_HIGH = THREE_KIND_VAL
            FULL_HOUSE_LOW = THREE_KIND_SECONDARY

        
        
        # Check for Straight
        # Initialize variables
        # Marker
        STRAIGHT = False
        # Highest card in the straight
        STRAIGHT_HIGH = 0
        # Temporary streak storage
        streak = 0
        # Max streak recorded
        streakMax = 0
        # Temporary streak set storage
        streakSet = [vals[0]]
        # Max streak set recorded (used for finding the straight high card)
        streakSetMax = [vals[0]]
        for i in range(12):
            # Look at two cards at a time
            # j is the first (lower)
            j = i % vals.__len__()
            # h is the second (higher)
            h = (i + 1) % vals.__len__()
            # initialize diff
            diff = 0
            # If our FIRST card is an ace, treat it like a 1
            if vals[j] == 14:
                diff = vals[h]-1
            # Otherwise get the diff normally
            else:
                diff = vals[h]-vals[j]
            # If our diff is 1 (sequential pair)
            if diff == 1:
                # If our first card is Ace, we break the chain
                # (Ace cannot act as BOTH 1 and 14 in the same straight)
                if vals[j] == 14:
                    streak = 2
                    streakSet = [vals[j], vals[h]]
                # Otherwise, increment the streak counter and append to the streak set
                else:
                    streak += 1
                    streakSet.append(vals[h])
                # If this is the longest streak so far, update the max values
                if streak > streakMax:
                    streakMax = streak
                    streakSetMax = streakSet
            # If these are duplicates, no change
            elif diff == 0:
                streak += 0
            # If not sequential or duplicates, break the chain and start again
            else:
                streak = 1
                streakSet = [vals[h]]
        # If the streak is 5 or more, we have a straight
        if streakMax >= 5:
            STRAIGHT = True
        STRAIGHT_HIGH = streakSetMax[-1]


        # Sort cards for straight flush checking
        cards.sort(key=lambda x: x.value)


        # Check for straight flush
        # Initialize variables
        # Marker
        STRAIGHT_FLUSH = False
        # Highest card in the straight flush
        STRAIGHT_FLUSH_HIGH = 0
        # Subset of cards all of the suit of the flush
        flushCards = []
        # Only calculate if a flush is present
        if FLUSH:
            for i in range(cards.__len__()):
                if cards[i].suit == FLUSH_SUIT:
                    # cards.pop(i)
                    flushCards.append(cards[i])
            
            flushStreak = 0
            # Temporary streak storage
            flushStreakMax = 0
            # Max streak recorded
            flushStreakSet = [flushCards[0]]
            # Temporary streak set storage
            flushStreakSetMax = [flushCards[0]]
            # Max streak set recorded (used for finding the straight high card)
            for i in range(flushCards.__len__() * 2):
                # Look at two cards at a time
                # j is the first (lower)
                j = i % flushCards.__len__()
                # h is the second (higher)
                h = (i + 1) % flushCards.__len__()
                # initialize diff
                diff = 0
                
                # If our FIRST card is an ace, treat it like a 1
                if flushCards[j].value == 14:
                    diff = flushCards[h].value - 1
                # Otherwise get the diff normally
                else:
                    diff = flushCards[h].value - flushCards[j].value
                
                if diff == 1:
                    # If our first card is Ace, we break the chain
                    # (Ace cannot act as BOTH 1 and 14 in the same straight)
                    if flushCards[j].value == 14:
                        flushStreak = 2
                        flushStreakSet = [flushCards[j].value,flushCards[h].value]
                    # Otherwise, increment the streak counter and append to the streak set
                    else:
                        flushStreak += 1
                        flushStreakSet.append(flushCards[h].value)
                    # If this is the longest streak so far, update the max values
                    if flushStreak > flushStreakMax:
                        flushStreakMax = flushStreak
                        flushStreakSetMax = flushStreakSet
                # If these are duplicates, no change
                # This should never happen, because it would require two cards of the same suit and value...
                elif diff == 0:
                    flushStreak += 0
                # If not sequential or duplicates, break the chain and start again
                else:
                    flushStreak = 1
                    flushStreakSet = [flushCards[h].value]
                
            # If the streak is 5 or more, we have a straight
            if flushStreakMax >= 5:
                STRAIGHT_FLUSH = True
            STRAIGHT_FLUSH_HIGH = flushStreakSetMax[-1]
            

        # Scoring time
        score = 0
        # Royal Flush == 1000 points
        # Straight Flush == 900 points + high card value
        # Four of a kind == 800 points + quad card value
        # Full house == 700 points + triple card value + (double card value / 10) 
        # Flush == 600 points + card values in descending order in descending powers of 10
        # Straight == 500 points + high card value
        # Three of a kind == 400 points + triple card value
        # Two pair == 300 points + high double value + (low double value / 10)
        # One pair == 200 points + double value
        # High card == 100 points + high card value

        # Royal Flush == 1000 points
        if STRAIGHT_FLUSH and STRAIGHT_FLUSH_HIGH == 14:
            score = 1000
        # Straight Flush == 900 points + high card value
        elif STRAIGHT_FLUSH:
            score = 900 + STRAIGHT_FLUSH_HIGH
        # Four of a kind == 800 points + quad card value
        elif FOUR_KIND:
            score = 800 + FOUR_KIND_VAL
        # Full house == 700 points + triple card value + (double card value / 100) 
        elif FULL_HOUSE:
            score = 700 + FULL_HOUSE_HIGH + FULL_HOUSE_LOW/100
        # Flush == 600 points + high card value + next high card value / 100 + next high card value / 10000 + etc.
        elif FLUSH:
            score = 600 + flushSet[0] + flushSet[1]/100 + flushSet[2]/10000 + flushSet[3]/1000000 + flushSet[4]/100000000
        # Straight == 500 points + high card value
        elif STRAIGHT:
            score = 500 + STRAIGHT_HIGH
        # Three of a kind == 400 points + triple card value
        elif THREE_KIND:
            score = 400 + THREE_KIND_VAL
        # Two pair == 300 points + high double value + (low double value / 100)
        elif TWO_PAIRS:
            score = 300 + TWO_PAIRS_HIGH + TWO_KIND_VAL/100
            # print(f"TWO_PAIRS_HIGH: {TWO_PAIRS_HIGH}")
            # print(f"TWO_KIND_VAL: {TWO_KIND_VAL}")
        # One pair == 200 points + double value
        elif TWO_KIND:
            score = 200 + TWO_KIND_VAL
        # High card == 100 points + high card value
        else:
            score = 100 + HIGH_CARD

        # OUTDATED::::Ties will be broken by whichever player has the higher cards in hand
        # NOTE: Ties will result in split pot now
        return score

        

    def runRound(self):
        # Define some variables
      
        for i in range(self.players.__len__()):
            self.board.playersFolding.append(False)
   
        phase = 0


        # Small and Big blinds mandatory pay in
        # Normal Poker
        if self.players.__len__() > 2:
            # Small blind
            self.board.pot += self.players[(self.buttonPlayerIndex + 1) % self.players.__len__()].bet(self.minBet / 2)
            # Big blind
            self.board.pot += self.players[(self.buttonPlayerIndex + 2) % self.players.__len__()].bet(self.minBet)
            # Under the gun
            self.board.activePlayerIndex = (self.buttonPlayerIndex + 3) % self.players.__len__()
        # HEADS UP POKER
        else:
            # Dealer is small blind
            self.board.pot += self.players[(self.buttonPlayerIndex) % self.players.__len__()].bet(self.minBet / 2)
            # Other is big blind
            self.board.pot += self.players[(self.buttonPlayerIndex + 1) % self.players.__len__()].bet(self.minBet)
            # Dealer is under the gun
            self.board.activePlayerIndex = (self.buttonPlayerIndex) % self.players.__len__()

        # Deal cards
        for i in range(self.players.__len__() * 2):
            self.players[(i+1+self.buttonPlayerIndex) % self.players.__len__()].deal(self.deck.top())
        
        

        
        if self.players.__len__() > 2:
            self.board.playerBets[(self.buttonPlayerIndex + 1) % self.players.__len__()] = self.minBet / 2
            self.board.playerBets[(self.buttonPlayerIndex + 2) % self.players.__len__()] = self.minBet
        else: 
            self.board.playerBets[self.buttonPlayerIndex] = self.minBet / 2
            self.board.playerBets[(self.buttonPlayerIndex + 1) % self.players.__len__()] = self.minBet

        # Phases:
        # Phase 1: no community cards
        # Phase 2: 3 community cards
        # Phase 3: 4 community cards
        # Phase 4: 5 community cards
        
        # Start in phase 1
        phase = 1
        while phase < 5:
        # while self.board.phase < 5:
            # Checking is enabled at the start of each phase
            # Exception, you cannot check unless the incoming bet is 0,
            # meaning that only the big-blind can check in the pre-flop

            # allow for checking at the beginning of each phase
            self.checkFlag = True
            self.board.checkFlag = True
    

            for i in range(self.players.__len__()):
                if not self.board.playersFolding[i]:
                    self.board.playersPassing[i] = False
            # Handle the small blind going first in every phase after the first
            if not phase == 1:
            # if not self.board.phase == 1:
                if self.players.__len__() > 2:
                    self.board.activePlayerIndex = self.buttonPlayerIndex + 1
                else:
                    self.board.activePlayerIndex = self.buttonPlayerIndex

            # If a player is out of chips
            for i in range(self.players.__len__()):
                if self.board.players[i].chips <= 0.0:
                    self.board.playersAllIn[i] = True

            # If only one player is not folding or all-in, players are passing manditorily
            activePlayerCount = 0
            for i in range(self.players.__len__()):
                if not self.board.playersFolding[i] and not self.board.playersAllIn[i]:
                    activePlayerCount += 1

            # Phases change once every player is folded or passing
            passing = True if activePlayerCount<=1 else False

            # i = activePlayerIndex
            while (not passing):
                # Table turn cycle:

                # Handle folded players
                if self.board.playersFolding[self.board.activePlayerIndex]:
                    # print(f"Player {players[self.board.activePlayerIndex].id} has folded.")
                    self.board.playersPassing[self.board.activePlayerIndex] = True
                    # Increment turn!
                    self.board.activePlayerIndex += 1
                    # Handle overflow
                    self.board.activePlayerIndex = (self.board.activePlayerIndex) % self.players.__len__()
                    continue

                if self.board.playersAllIn[self.board.activePlayerIndex]:
                    self.board.playersPassing[self.board.activePlayerIndex] = True
                    # Increment turn!
                    self.board.activePlayerIndex += 1
                    # Handle overflow
                    self.board.activePlayerIndex = (self.board.activePlayerIndex) % self.players.__len__()
                    continue
                # Print player interface
                # print(f"Player {players[self.board.activePlayerIndex].id}, it is your turn.")

                # REFNOTE: This sequence of code is reused elsewhere, it would be a good method for the round class
                incomingBet = self.board.currentBet - self.board.playerBets[self.board.activePlayerIndex]
                
                # Determine what actions are available to the player
                validActions = self.getValidPlayerActions(incomingBet,self.board.activePlayerIndex)
                
                # Get the choice of action from player object
                action = self.players[self.board.activePlayerIndex].get_action(self.board,validActions)
               
                
                # Also, currently actions are only accepted on the command line, perhaps a method in the
                # Player class could be used to determine what type of input should be used (command line
                # for real players, the appropriate decision making method for agent players, etc.) once
                # the class recieves it's rework.

                # Handle player action
                if action in [Action.MIN_BET,Action.LOW_BET,Action.MID_BET,Action.HIGH_BET]:
                    self.handleBet(action,self.board.activePlayerIndex,incomingBet)
                elif action == Action.ALL_IN:
                    self.handleAllIn(self.board.activePlayerIndex)
                elif action == Action.OP_MAX:
                    self.handleOpMax(self.board.activePlayerIndex,incomingBet)
                elif action == Action.CALL:
                    self.handleCall(self.board.activePlayerIndex,incomingBet)
                elif action == Action.CHECK:
                    # Passing
                    self.board.playersPassing[self.board.activePlayerIndex] = True
                elif action == Action.FOLD:
                    if not self.supressOuptut:
                        print("You have folded")
                    # Folded
                    self.board.playersFolding[self.board.activePlayerIndex] = True
                    # Passing
                    self.board.playersPassing[self.board.activePlayerIndex] = True
                else:
                    if not self.supressOuptut:
                        print("Try again")
                    continue

                # print(f"Players Passing: {self.board.playersPassing}")

                # Increment turn!
                self.board.activePlayerIndex += 1
                # Handle overflow
                self.board.activePlayerIndex = (self.board.activePlayerIndex) % self.players.__len__()
                
                # Check Condition!
                passing = True
                # If any of the players are not passive, continue this phase
                for j in range(self.board.playersPassing.__len__()):
                    if self.board.playersPassing[j] == False:
                        passing = False
                # If only one player is NOT folding, players are passing manditorily
                notFoldCount = 0
                for i in range(self.players.__len__()):
                    if not self.board.playersFolding[i]:
                        notFoldCount +=1
                if notFoldCount == 1:
                    passing = True
                
                # print(passing)
            
            # Handle phase change
            # Phase 1-->2 Preflop --> Flop
            if phase == 1:
            # if self.board.phase == 1:
                self.board.community.append(self.deck.top())
                self.board.community.append(self.deck.top())
                self.board.community.append(self.deck.top())
            # Phase 2-->3 Flop --> Turn
            # Phase 3-->4 Turn --> River
            elif phase == 2 or phase == 3:
            # elif self.board.phase == 2 or self.board.phase == 3:
                self.board.community.append(self.deck.top())
            # Phase 4-->5 River --> Scores
            elif phase == 4:
            # elif self.board.phase == 4:
                if not self.supressOuptut:
                    print("Time for the results!")
            # This should never occur, the prints are for debuggging in case it does
            else:
                if not self.supressOuptut:
                    print("SOMETHING HAS GONE WRONG WITH THE PHASES!")
                    print(f"THIS WAS PHASE {phase}!!!")

            # REFNOTE: Eventually this might become unnecessary due to the functionality
            # of checking score being planned to move to the Engine class instead of the
            # player class... but if we want the agent to be able to calculate odds of hands
            # and such, the agent would need to know the community cards, so it might not be
            # worth removing the community knowledge from the players just yet.
            
            # No longer needed as of now
            # # Update each player's knowledge of the community cards
            # for i in range(self.players.__len__()):
            #     self.players[i].communityUpdate(self.board.community)
            
            # Change phase
            phase += 1
            # Update the board phase so that players/agents can see it
            self.board.phase += 1

        # Check the score of each player's hand
        scores = []
        for i in range(self.players.__len__()):
            # Folding players get 0 points
            if self.board.playersFolding[i]:
                scores.append(0)
            # Scores are calculated by the player objects
            else:
                # REFNOTE: This could change to being done by the Engine, taking
                # each players 2 card hand and the community cards into account 
                scores.append(self.handScore(i))
        
        # Find winners
        maxScore = -1
        winningIndex = []
        for i in range(self.players.__len__()):
            if scores[i] > maxScore:
                maxScore = scores[i]
                winningIndex = [i]
            # There can be multiple Players with equal strength best hands
            elif scores[i] == maxScore:
                winningIndex.append(i)
        
        # REFNOTE: This sequence of code is reused elsewhere, it would be a good method for the round class
        communityString = "["
        for card in self.board.community:
            communityString += f"{card}, "
        if self.board.community.__len__() > 0:
            communityString = communityString[:-2] + "]"
        else:
            communityString += "]"

        # Print player scores and hands (along with community cards for context)
        if not self.supressOuptut:
            print()
            print(f"River State: {communityString}")
            print()
            print(f"Player Scores/Hands:")
            for i in range(self.players.__len__()):
                print(f"Player {self.players[i].id} score: {scores[i]}")
                print(f"\t hand: " + ", ".join(str(card) for card in self.players[i].cardsInHand))
        
        # If there are multiple winners, tie-break by cards in hand
        if winningIndex.__len__() > 1:
            # Display information about multiple winners
            if not self.supressOuptut:
                print(f"The winners are:")
                for i in winningIndex:
                    print(f"Player {self.players[i].id}")
            
            # NOTE: The commented code from here until the other note is the tie-breaker functionality.
            #       It is not being used due to ties resulting in split pots being normal poker rules.
            # # Identify tie-break scores
            # tieScores = []
            # for i in range(self.players.__len__()):
            #     # If not a winner, no tiebreak score
            #     if i not in winningIndex:
            #         tieScores.append(0)
            #     # If a winner, calculate tie-break score
            #     else:
            #         temp = self.players[i].cardsInHand
            #         temp.sort(key=lambda x: x.value, reverse = True)
            #         # tie-break score = high card value * 10 + low card value
            #         tieScores.append(temp[0].value * 10 + temp[1].value)
            
            # # Display information about tie-breaker hands
            # if not self.supressOuptut:
            #     print("Tie Breaker Hands:")
            #     for i in winningIndex:
            #         print(f"Player {self.players[i].id} hand: "+ ", ".join(str(card) for card in self.players[i].cardsInHand))

            # # Find winners
            # tiebreaker = -1
            # tieWinningIndex = []
            # for i in winningIndex:
            #     if tieScores[i] > tiebreaker:
            #         tiebreaker = tieScores[i]
            #         tieWinningIndex = [i]
            #     # There can be multiple Players with equal strength hands
            #     elif tieScores[i] == tiebreaker:
            #         tieWinningIndex.append(i)

            # # Display information about who won the tie-break
            # winningIndex = tieWinningIndex
            # if not self.supressOuptut:
            #     if winningIndex.__len__() == 1:
            #         print(f"The tiebreak winner is: Player {winningIndex[0] + 1}")
            #     else:
            #         print(f"The tiebreak winners are:")
            #         for i in winningIndex:
            #             print(f"Player {self.players[i].id}")
            # NOTE: End of tie-break functionality
            
        else: 
            # Display information about who won the pot
            if not self.supressOuptut:
                print(f"The winner is: Player {winningIndex[0] + 1}")
        
        # Display pot won
        if not self.supressOuptut:
            print(f"The pot won is: {self.board.pot} chips!!!")

        # Display how much each winner won
        if winningIndex.__len__() == 1:
            self.players[winningIndex[0]].win_round(self.board.pot)
            if not self.supressOuptut:
                print(f"Player {self.players[winningIndex[0]].id} wins {self.board.pot} chips!")
        else:
            numWinners = winningIndex.__len__()
            for i in winningIndex:
                self.players[winningIndex[i]].win_round(self.board.pot/numWinners)
                if not self.supressOuptut:
                    print(f"Player {self.players[winningIndex[i]].id} wins {self.board.pot/numWinners} chips!")
        
        # Clean players hands and bets
        for i in range(self.players.__len__()):
            self.players[i].cardsInHand = []
            self.players[i].current_bet = 0

        # Eliminate players as necessary, and update Dealer Button
        temp = []
        for i in range(self.players.__len__()):
            # If a player has remaining chips greater than or equal to the minimum bet,
            # they continue to the next round, otherwise they are eliminated
            if self.players[i].chips >= self.minBet:
                temp.append(self.players[i])
            # If the dealer is to be eliminated, move the button one spot to the right.
            elif i == self.buttonPlayerIndex:
                self.buttonPlayerIndex -= 1
        # The dealer button moves to the left
        self.buttonPlayerIndex += 1
        self.buttonPlayerIndex = self.buttonPlayerIndex % temp.__len__()

        # REFNOTE: in the Round class that is likely going to be added, the primary method
        # of the Round class used by the main poker engine class should return the updated
        # player arraylist (with updated chip counts, blank community cards and hands, etc.)
        # so that if players are eliminated, the poker engine can communicate that to the
        # next round.

        # Before self.players is updated, record the chip totals of every player in this round
        for i in range(self.players.__len__()):
            self.players[i].recordChips()
            # print(f"Player {self.players[i].id} record: {self.players[i].chipRecord}")

        # Eliminate players in object field
        self.players = temp
        if not self.supressOuptut:
            print()
            input("Next Round (hit enter to continue)")

        return self.players, self.buttonPlayerIndex
    
    
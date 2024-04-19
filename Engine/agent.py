from player import Player
from player import Action
from abc import ABC, abstractmethod

class Agent(Player):

    @abstractmethod
    def get_action(self, board, validActions):
        pass 
    
    def handScore(hand):
        # Consolidate cards
        cards = hand

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
            j = i % 7
            # h is the second (higher)
            h = (i + 1) % 7
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
            for i in range(7):
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
        # One pair == 200 points + double value
        elif TWO_KIND:
            score = 200 + TWO_KIND_VAL
        # High card == 100 points + high card value
        else:
            score = 100 + HIGH_CARD

        # Ties will be broken by whichever player has the higher cards in hand
        return score
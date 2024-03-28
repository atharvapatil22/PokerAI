class PokerPlayer:

    def __init__(self, chips, id) -> None:
        # Hand should be 2 cards in poker
        self.handCards = []
        # Chips with which to bet
        self.chips = chips
        # Cards all players can see (need each player to be able to view it right?)
        # Community functionality might be redundant
        self.community = []
        # Id for player number tracking (1-->?)
        self.id = id

    # Adds the passed card to the player's hand
    def dealt(self, card):
        self.handCards.append(card)
    
    # Replaces the player's community card knowledge with the passed array of cards
    def communityUpdate(self, cards):
        self.community = cards

    # Removes the amount listed from the player's chips and returns it
    def bet(self, chips):
        self.chips -= chips
        return chips
    
    # Adds the amount listed to the player's chips
    def wins(self,chips):
        self.chips += chips

    # Returns a neat string of the player's hand of cards
    def hand(self):
        temp = "["
        for card in self.handCards:
            temp += f"{card}, "
        temp = temp[:-2] + "]"
        return temp
    
    # Returns the score of the best hand the player can make given their hand and the community cards
    def handScore(self):
        # Consolidate cards
        cards = self.handCards + self.community


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

        
        # WARNING: THE STRAIGHT LOGIC HERE IS WRONG, ACE CANNOT BRIDGE KING AND TWO IN A STRAIGHT
        
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
        streakSetMax = []
        for i in range(12):
            j = i % 7
            h = (i + 1) % 7
            diff = 0
            if vals[j] == 14:
                diff = vals[h]-1
            else:
                diff = vals[h]-vals[j]
            if diff == 1:
                streak += 1
                streakSet.append(vals[h])
                if streak > streakMax:
                    streakMax = streak
                    streakSetMax = streakSet
            elif diff == 0:
                streak += 0
            else:
                streak = 1
                streakSet = [vals[h]]
        streakSetMax.sort()
        if streakMax >= 5:
            STRAIGHT = True
        STRAIGHT_HIGH = streakSetMax[-1]


        # Sort cards for straight flush checking
        cards.sort(key=lambda x: x.value)

        # WARNING: THE STRAIGHT LOGIC HERE IS WRONG, ACE CANNOT BRIDGE KING AND TWO IN A STRAIGHT

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
                if not cards[i].suit == FLUSH_SUIT:
                    # cards.pop(i)
                    flushCards.append(cards[i])
            
            flushStreak = 0
            # Temporary streak storage
            flushStreakMax = 0
            # Max streak recorded
            flushStreakSet = [flushCards[0]]
            # Temporary streak set storage
            flushStreakSetMax = []
            # Max streak set recorded (used for finding the straight high card)
            for i in range(flushCards.__len__() * 2):
                j = i % flushCards.__len__()
                h = (i + 1) % flushCards.__len__()
                diff = 0
                if flushCards[j].value == 14:
                    diff = flushCards[h].value - 1
                else:
                    diff = flushCards[h].value - flushCards[j].value
                
                if diff == 1:
                    flushStreak += 1
                    flushStreakSet.append(flushCards[h].value)
                    if flushStreak > flushStreakMax:
                        flushStreakMax = flushStreak
                        flushStreakSetMax = flushStreakSet
                elif diff == 0:
                    flushStreak += 0
                else:
                    flushStreak = 1
                    flushStreakSet = [flushCards[h].value]
                
            if flushStreakMax >= 5:
                STRAIGHT_FLUSH = True
            flushStreakSetMax.sort()
            # CURRENTLY DOES NOT COUNT FOR ROYAL FLUSH PROPERLY
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
        # Full house == 700 points + triple card value + (double card value / 10) 
        elif FULL_HOUSE:
            score = 700 + FULL_HOUSE_HIGH + FULL_HOUSE_LOW/10
        # Flush == 600 points + high card value
        elif FLUSH:
            # THERE COULD BE AN INNACCURACY HERE
            # score = 600 + FLUSH_HIGH
            score = 600 + flushSet[0] + flushSet[1]/10 + flushSet[2]/100 + flushSet[3]/1000 + flushSet[4]/10000
        # Straight == 500 points + high card value
        elif STRAIGHT:
            score = 500 + STRAIGHT_HIGH
        # Three of a kind == 400 points + triple card value
        elif THREE_KIND:
            score = 400 + THREE_KIND_VAL
        # Two pair == 300 points + high double value + (low double value / 10)
        elif TWO_PAIRS:
            score = 300 + TWO_PAIRS_HIGH + TWO_KIND/10
        # One pair == 200 points + double value
        elif TWO_KIND:
            score = 200 + TWO_KIND_VAL
        # High card == 100 points + high card value
        else:
            score = 100 + HIGH_CARD

        # Ties will be broken by whichever player has the higher cards in hand
        return score
        
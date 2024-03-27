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

    def dealt(self, card):
        self.handCards.append(card)
    
    def communityUpdate(self, cards):
        self.community = cards

    def bet(self, chips):
        self.chips -= chips
        return chips
    
    def wins(self,chips):
        self.chips += chips

    def hand(self):
        temp = "["
        for card in self.handCards:
            temp += f"{card}, "
        temp = temp[:-2] + "]"
        return temp
    
    def handScore(self):
        cards = self.handCards + self.community

        temp = []
        suits = []
        SUITS = ["Spades", "Clubs", "Diamonds", "Hearts"]
        for card in cards:
            temp.append(card.value)
            suits.append(card.suit)
        temp.sort()
        cards.sort(key=lambda x: x.value)
        
        

        # Check for Straight
        STRAIGHT = False

        streak = 0
        streakMax = 0
        STRAIGHT_HIGH = 0
        streakSet = [temp[0]]
        streakSetMax = []
        for i in range(12):
            j = i % 7
            h = (i + 1) % 7
            diff = 0
            if temp[j] == 14:
                diff = temp[h]-1
            else:
                diff = temp[h]-temp[j]
            if diff == 1:
                streak += 1
                streakSet.append(temp[h])
                if streak > streakMax:
                    streakMax = streak
                    streakSetMax = streakSet
            elif diff == 0:
                streak += 0
            else:
                streak = 1
                streakSet = [temp[h]]
        streakSetMax.sort()
        if streakMax >= 5:
            STRAIGHT = True
        STRAIGHT_HIGH = streakSetMax[-1]

            
    

        


        # Check for Flush
        FLUSH = False
        FLUSH_HIGH = 0
        FLUSH_SUIT = ""
        flushSet = []
        for suit in SUITS:
            if suits.count(suit) >=5:
                FLUSH = True
                FLUSH_SUIT = suit
                for card in cards:
                    if card.suit == suit and card.value > FLUSH_HIGH:
                        FLUSH_HIGH = card.value
                    if card.suit == suit:
                        flushSet.append(card.value)
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
        for i in range(13):
            val = i + 2
            if temp.count(val) == 4:
                FOUR_KIND = True
                FOUR_KIND_VAL = val
            elif temp.count(val) == 3:
                THREE_KIND = True
                THREE_KIND_VAL = val
            elif temp.count(val) == 2:
                if TWO_PAIRS:
                    TWO_KIND_VAL = TWO_PAIRS_HIGH
                    TWO_PAIRS_HIGH = val
                elif TWO_KIND:
                    TWO_PAIRS = True
                    TWO_PAIRS_HIGH = val
                else:
                    TWO_KIND = True
                    TWO_KIND_VAL = val
        
    
        # Check for Full house
        FULL_HOUSE = False
        FULL_HOUSE_HIGH = 0
        FULL_HOUSE_LOW = 0
        if THREE_KIND and TWO_PAIRS:
            FULL_HOUSE = True
            FULL_HOUSE_HIGH = THREE_KIND_VAL
            FULL_HOUSE_LOW = TWO_PAIRS_HIGH
        elif THREE_KIND and TWO_KIND:
            FULL_HOUSE = True
            FULL_HOUSE_HIGH = THREE_KIND_VAL
            FULL_HOUSE_LOW = TWO_KIND_VAL

        
        # Note High Card
        HIGH_CARD = temp[-1]

        # Check for straight flush
        STRAIGHT_FLUSH = False
        STRAIGHT_FLUSH_HIGH = 0
        flushCards = []
        if FLUSH:
            for i in range(7):
                if not cards[i].suit == FLUSH_SUIT:
                    # cards.pop(i)
                    flushCards.append(cards[i])
            
            flushStreak = 0
            flushStreakMax = 0
            flushStreakSet = [flushCards[0]]
            flushStreakSetMax = []
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
        

        
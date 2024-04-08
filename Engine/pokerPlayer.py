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
    
    # Returns player's hand cards
    def handCards(self):
        return self.handCards
    
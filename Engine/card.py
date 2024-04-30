class Card:
    SUITS = ["Spades", "Clubs", "Diamonds", "Hearts"]

    def __init__(self, value, suit):
        self.value = value
        self.face = True if value > 10 else False
        self.suit = suit
        self.id = self.value + self.SUITS.index(self.suit) * 13

    def __str__(self) -> str:
        temp = ""
        if self.value == 14:
            temp = "A"
        elif self.value == 13:
            temp = "K"
        elif self.value == 12:
            temp = "Q"
        elif self.value == 11:
            temp = "J"
        elif self.value == 10:
            temp = "T"
        else:
            temp = self.value.__str__()
        
        if self.suit == "Spades":
            # temp = temp + " ♠"
            temp = temp + " Sp"
        elif self.suit == "Clubs":
            # temp = temp + " ♣"
            temp = temp + " Cl"
        elif self.suit == "Diamonds":
            # temp = temp + " ♦"
            temp = temp + " Di"
        elif self.suit == "Hearts":
            # temp = temp + " ♥"
            temp = temp + " He"
        else:
            temp = temp + " INVALID SUIT"
        
        return temp

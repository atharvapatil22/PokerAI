from card import Card
import random

class Deck:
    SUITS = ["Spades", "Clubs", "Diamonds", "Hearts"]

    def __init__(self):
        self.cards = []
        for suit in self.SUITS :
            for i in range(13):
                self.cards.append(Card(i+2, suit))

    def shuffle(self):
        random.shuffle(self.cards)

    def top(self):
        return self.cards.pop()

    
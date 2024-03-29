from card import Card
import random

class Deck:
    SUITS = ["Spades", "Clubs", "Diamonds", "Hearts"]

    def init(self, shuffleFlag = True, deckSequence = None):
        self.cards = []
        if shuffleFlag:
            for suit in self.SUITS :
                for i in range(13):
                    self.cards.append(Card(i+2, suit))
            self.shuffle()
        else:
            # Parse deckSequence
            # Each card will be in the form: "[<#|T|J|Q|K|A> <Sp|Cl|Di|He>]"
            for cardString in deckSequence:
                # Remove the brackets
                cardString = cardString[1:-1]
                valString, suitShort = cardString.split(" ")
                val = 0
                suit = ""
                # Parse val
                # If the TJQKA gets canned, JUST USE THE ELSE, it'll work on numbers
                if valString == "T":
                    val = 10
                elif valString == "J":
                    val = 11
                elif valString == "Q":
                    val = 12
                elif valString == "K":
                    val = 13
                elif valString == "A":
                    val = 14
                else:
                    val = int(valString)
                
                # Parse suit
                if suitShort == "Sp":
                    suit = "Spades"
                elif suitShort == "Cl":
                    suit = "Clubs"
                elif suitShort == "Di":
                    suit = "Diamonds"
                elif suitShort == "He":
                    suit = "Hearts"
                self.cards.append(Card(val, suit))
            # Reverse so that the cards are drawn in the order specified in the deckSequence
            self.cards.reverse()

    def shuffle(self):
        random.shuffle(self.cards)

    def top(self):
        return self.cards.pop()

    
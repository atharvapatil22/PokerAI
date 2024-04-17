from card import Card
import random

class Deck:
    SUITS = ["Spades", "Clubs", "Diamonds", "Hearts"]

    def __init__(self, shuffleFlag = True, deckSequence = None):
        self.cards = []
        if shuffleFlag:
            for suit in self.SUITS :
                for i in range(13):
                    self.cards.append(Card(i+2, suit))
            self.shuffle()
        else:
            # print(deckSequence)
            # Parse deckSequence
            # Each card will be in the form: "'<#|T|J|Q|K|A> <Sp|Cl|Di|He>'"
            for cardStringIdx in range(len(deckSequence)): #each card in the deck provided where deck is list of cards
                # Remove the ',' at the end
                cardString = deckSequence[cardStringIdx]
                # print(cardString)
                # if cardStringIdx < len(deckSequence) - 1: #if not last card, remove the trialing ','
                #     cardString = cardString[:-1]
                valString, suitShort = cardString.split(" ") #separate value and suite
                #remove trailing \'
                valString = valString[1:]
                suitShort = suitShort[:-1] 
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

    
from pokerPlayer import PokerPlayer
from deck import Deck
from round import Round

# general idea, poker will have rounds that take players array as parameters and return players array 
# play will continue until self.players array has size 1
# Within the rounds (might make a class for that), the rules of poker will be interpreted (might make a rules class???)
# So the button shenanigains (autobets) & turn order will be controlled from there. On each player's turn they can do the
# standard poker actions. Once everyone is neutral, the next community cards "stage" will begin, and the priority passing will continue.
# once everyone is done on the last stage, the score of hands will be calculated (using rules), and the player who wins will have the 
# pot added to their chips. Players with 0 remaining chips (or less chips than the minBet I guess?) will be removed from the players array
# and that array will be returned from the primary method of the Round

class Poker:

    def __init__(self, numPlayers, startChips, minBet) -> None:
        self.players = []
        for i in range(numPlayers):
            self.players.append(PokerPlayer(startChips, i+1))
        self.minBet = minBet
        self.buttonPlayerIndex = 0

    # This is the primary method of the poker engine class
    # Running this method runs the game to completion
    def runGame(self):
        # Rounds continue until only one player is left
        # That player is the winner
        round = Round(self.players, self.minBet, self.buttonPlayerIndex)
        while self.players.__len__() > 1:
            self.players = round.runRound()
        
        print(f"THE WINNER IS: PLAYER {self.players[0].id}")


testGame = Poker(numPlayers = 2,startChips = 100, minBet = 2)

testGame.runGame()


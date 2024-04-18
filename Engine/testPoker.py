# General Idea: the test class will parse test data to provide to poker.py,
# and will create players to pass into poker.py based on what kinds of players we want playing the game.
# Poker will be modified to take an array of Decks (one for each round), and an array of players
# The players' starting chips should be zero here, as they will be set to 100 at the start of each game.
# The player class will be modified to have a gameNumber and roundNumber variables that will be incremented when appropriate
# to allow for the 2D array of chip balance per game/round to be stored. This way we have some tangible data to
# display as results.
from deck import Deck
from poker import Poker
from player import Player
from realPlayer import RealPlayer

class TestPoker:

    # NFNF
    # startChips: value of startChips used to create poker games
    # minBet: value of minBet used to create poker games
    # players: array of players to pass into poker games
    # playerIDCount: used to track player ID for player creation, the ID is used to distinguish between player types
    # pokerGameDeckSequences: used to store the deck sequences to pass to each poker game. [[<deck sequence>, <deck Sequence>, etc.],[etc.]]
    def __init__(self, startChips, minBet):
        self.startChips = startChips
        self.minBet = minBet
        self.initPlayers = []
        self.players = []
        self.playerIDCount = 1
        self.pokerGameDeckSequences = []

    
    def parseFile(self, testFile):
        
        squenceSrc = open(testFile, "r")
        squences = squenceSrc.readlines()
        # print(squences)

        for games in squences: #over all possible games
            game = [] #collect all sqs in a game
            gamesqs = list(games.split("[")[1:]) #remove game number formatting and isolate game sequences
            # if firstSeq:
            #     print(gamesqs)
            for sqs in range(len(gamesqs)): #for each deck available in the sequence
                if sqs < len(gamesqs) - 1: #if not last sequence
                    cards = gamesqs[sqs][:-3] #remove the trailing brackets with trailing ','
                else:
                    cards = gamesqs[sqs][:-2] #remove trailing ] in last sequence
                # if firstSeq:
                #     print(cards)
                #     firstSeq = False
                cards = cards.split(', ')
                game.append(Deck(False, cards)) #add current sequence to associated game

                # Game will be passed to poker, as it is an array of decks, one for each round.

            self.pokerGameDeckSequences.append(game) #add game
        print('all decks created')
        squenceSrc.close()

        return self.pokerGameDeckSequences
    
    def runTest(self):
        for i in range(self.pokerGameDeckSequences.__len__()):
            pokerInstance = Poker(self.players, self.startChips, self.minBet, False, self.pokerGameDeckSequences[i])
            newPlayers = pokerInstance.runGame()
            # Handle new information about players here if necessary
            self.players = newPlayers
            if self.players.__len__() == 1:
                break

        return self.players

###### NOTE: Agent functionality has not yet been implmented.
###### once agents have been implemneted, the options for adding agents to this test class will be added

    def addRealPlayer(self):
        temp = RealPlayer(self.playerIDCount, 0)
        self.initPlayers.append(temp)
        self.players.append(temp)
        self.playerIDCount += 1

###### DEFAULT OPTIONS:
print("hello")
test = TestPoker(100, 2)
test.addRealPlayer()
test.addRealPlayer()
# test.parseFile("../Testing/test_sequencesRound.txt")
test.parseFile("../Testing/test_sequencesRound3.txt")
test.runTest()

print("RESULT")
for i in range(test.players.__len__()):
    print(f"Player {test.players[i].id} record: {test.players[i].chipRecord}")
print("INITIAL")
for i in range(test.initPlayers.__len__()):
    print(f"Player {test.initPlayers[i].id} record: {test.initPlayers[i].chipRecord}")


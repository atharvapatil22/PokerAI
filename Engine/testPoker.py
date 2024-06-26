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
from call_agent import CallAgent
from minimax_agent import MinimaxAgent

from monte_carlo_agent import MonteCarloAgent
from simulation_agent import SimulationAgent
from simple_probability_agent import SimpleProbabilityAgent

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
        p1_wins = 0
        p2_wins = 0
        for i in range(self.pokerGameDeckSequences.__len__()):
            # print("poker instance with players: ", self.players)
            pokerInstance = Poker(self.players, self.startChips, self.minBet, False, self.pokerGameDeckSequences[i], supressOutput=True)
            winner = pokerInstance.runGame()
            print(f"Game {i} complete")
            if winner.__len__() > 1 and (winner[1].chips > winner[0].chips):
                if winner[1].id == self.players[0].id:
                    p1_wins += 1
                else:
                    p2_wins += 1
                winner = [winner[1]]
            else:
                if winner[0].id == self.players[0].id:
                    p1_wins += 1
                else:
                    p2_wins += 1
            
            print(f"Winner was player {winner[0].id}")
            # Handle new information about players here if necessary
        print(f"Player 1 win percentage: {p1_wins / self.pokerGameDeckSequences.__len__()}")
        print(f"Player 2 win percentage: {p2_wins / self.pokerGameDeckSequences.__len__()}")
            
            

        return self.players

###### NOTE: Agent functionality has not yet been implmented.
###### once agents have been implemneted, the options for adding agents to this test class will be added

    def addRealPlayer(self):
        temp = RealPlayer(self.playerIDCount, 0)
        self.players.append(temp)
        self.playerIDCount += 1
    
    def addCallAgent(self):
        temp = CallAgent(self.playerIDCount, 0)
        self.players.append(temp)
        self.playerIDCount += 1
    
    def addMinMaxAgent(self):
        temp = MinimaxAgent(self.playerIDCount, 0)
        self.players.append(temp)
        self.playerIDCount += 1


    def addMonteAgent(self):
        temp = MonteCarloAgent(self.playerIDCount, 0)
        self.players.append(temp)
        self.playerIDCount += 1

    def addSimulationAgent(self):
        temp = SimulationAgent(self.playerIDCount, 0)
        self.players.append(temp)
        self.playerIDCount += 1

    def addSimpleProbabilityAgent(self):
        temp = SimpleProbabilityAgent(self.playerIDCount, 0)
        self.players.append(temp)
        self.playerIDCount += 1

###### DEFAULT OPTIONS:
test = TestPoker(100, 2)
# test.addRealPlayer()
# test.addRealPlayer()

# test.addCallAgent()
# test.addCallAgent()
# test.addCallAgent()
# test.addCallAgent()
test.addSimulationAgent()
test.addMonteAgent()
# test.addSimpleProbabilityAgent()
# test.addMinMaxAgent()





# test.parseFile("../Testing/test_sequencesRound.txt")
# test.parseFile("../Testing/test_sequencesRound3.txt")
test.parseFile("../Testing/test_sequences7.txt")
print("running test")
# test.runTest()
import cProfile


cProfile.run('test.runTest()')
print("RESULT")

output1 = open("../Testing/p1Output.txt", "w")
output2 = open("../Testing/p2Output.txt", "w")

print(f"Player {test.players[0].id} record: {test.players[0].chipRecord}", file=output1)
print(f"Player {test.players[1].id} record: {test.players[1].chipRecord}", file=output2)

output1.close()
output2.close()




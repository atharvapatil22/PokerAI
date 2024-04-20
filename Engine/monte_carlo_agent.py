from player import Player
from player import Action, BetRatio
from agent import Agent
from deck import Deck
# Get the Board from Round with Round.Board(<constructor arguments>)
from round import Round
import copy
from random import randrange

class MonteCarloAgent(Agent):

    def get_action(self, board, validActions):
        cards_in_hand = self.cardsInHand
        community_cards = board.community
        your_wins = 0
        opponent_wins = 0
        ties = 0
        simulations = 1000
        for _ in range(simulations):
            deck = Deck(True, None)
            for card_in_hand in cards_in_hand:
                for card in deck.cards:
                    if str(card) == str(card_in_hand):
                        deck.cards.remove(card)
                        break
            # print(len(deck.cards))
            opponent_hand = [deck.top(), deck.top()] + community_cards
            hand = cards_in_hand + community_cards
            randomized_community_cards = []
            for _ in range(5-len(community_cards)):
                randomized_community_cards.append(deck.top())
            opponent_hand += randomized_community_cards
            hand += randomized_community_cards
            hand_score = MonteCarloAgent.handScore(hand)
            opponent_score = MonteCarloAgent.handScore(opponent_hand)
            if hand_score > opponent_score:
                your_wins +=1
            elif hand_score == opponent_score:
                ties +=1
            else:
                opponent_wins +=1
        your_win_percentage = your_wins/(simulations-ties)        
        print(f"Your win percentage:", your_win_percentage)
        print(f"Opponent win percentage:", opponent_wins/(simulations-ties))
        if(your_win_percentage > 0.6):
            if(Action.MID_BET in validActions):
                return Action.MID_BET
            elif(Action.HIGH_BET in validActions):
                return Action.HIGH_BET
            else:
                return Action.ALL_IN
        elif(your_win_percentage > 0.4):
            if(Action.CHECK in validActions):
                return Action.CHECK
            return Action.CALL
        else:
            return Action.FOLD
        
    
    
    class MCTree:

        def __init__(self, boardState):

            self.root = MonteCarloAgent.MCNode(boardState, None, False, None)
            #NFNF

        # Use UCB1 Algorithm to select a leaf node from the tree to expand
        #   Go layer by layer, choose a node from the layer with the highest UCB1 Score
        #   If that node has any remaing actions in availableActions, select that node!
        #   Otherwise, the children of the chosen node become the next "layer".
        #   Repeat until you have a selected node :)
        def SELECT(self):
            # TODO
            # Certified recursion classic
            pass

        # Create child node for the selected leaf node based on valid game actions
        #   Choose the action to expand a node for at random
        def EXPAND(self, leaf):
            if leaf.availableActions.__len__() == 0:
                print("SOMETHING WENT WRONG!")
                return
            randomActionIdx = randrange(leaf.availableActions.__len__())
            randomAction = leaf.availableActions[randomActionIdx]
            newBoard = copy.deepcopy(leaf.board)
            # TODO: Perform the action on newBoard!!!
            # NOTE: This can likely be done by copying some methods from round, making them static, and then using them.
            #       These new static methods should be made in such a way that they can be used in the simulations too!

            newChild = MonteCarloAgent.MCNode(newBoard, leaf, not leaf.isAgent, leaf.availableActions.pop(randomActionIdx))

            leaf.children.append(newChild)
            

            pass

        # Run a simulation on the given node
        #   This is where a deck sequence is generated based off of what we know (board variable of node)
        #   Return [amount], where amount is the amount won in the round. (positive is win) (0 is tie (two player game)) (negative is loss)
        def SIMULATE(self, node):
            # TODO
            pass

        # Update the child win/loss/tie stats with the result,
        # and propagate the result to all ancestors of the child(simNode) (accounting for player change)
        def BACK_PROPAGATE(self, result, simNode):
            # TODO: Make the result propagate as well, storing amount of money won/lost
            # NOTE: The above TODO relies on functionality in the MCNode class that does not yet exist

            if result > 0:
                simNode.wins += 1
            elif result < 0:
                simNode.losses += 1
            else:
                simNode.ties += 1

            if simNode.parent is not None:
                self.BACK_PROPAGATE(simNode.parent)
            pass

        # This is a Static version of a function from round.py
        # Function will determine all the valid actions for the active player
        def getValidPlayerActions(self, board):
            # Copy all the player actions
            validActions = [member for _, member in Action.__members__.items()]
            # print("player index",board.activePlayerIndex)
            incomingBet = board.currentBet - board.playerBets[board.activePlayerIndex]
            if board.checkFlag and incomingBet == 0:
                # CANNOT CALL -> phase bet is 0
                validActions.remove(Action.CALL)
            elif incomingBet > board.players[int(board.activePlayerIndex)].chips:
                # CANNOT CALL -> Not enough chips
                validActions.remove(Action.CALL)
            if (not board.checkFlag) or incomingBet != 0:
                # CANNOT CHECK -> You must call, raise, or fold
                validActions.remove(Action.CHECK)
            if incomingBet + board.minBet > board.players[int(board.activePlayerIndex)].chips:
                # Not enough chips
                validActions.remove(Action.MIN_BET)
                validActions.remove(Action.LOW_BET)
                validActions.remove(Action.MID_BET)
                validActions.remove(Action.HIGH_BET)
            # OP_MAX action handling
            opponentIdx = (board.activePlayerIndex + 1) % board.players.__len__()
            if self.players[int(opponentIdx)].chips == 0:
                # Opponent is already all in
                validActions.remove(Action.OP_MAX)
                validActions.remove(Action.MIN_BET)
                validActions.remove(Action.MID_BET)
                validActions.remove(Action.HIGH_BET)
            if board.players[int(opponentIdx)].chips + incomingBet >= board.players[int(board.activePlayerIndex)].chips:
                # Not enough chips to overbet other player
                validActions.remove(Action.OP_MAX)
            else:
                # These actions would now overbet the opponent max
                validActions.remove(Action.ALL_IN)
                opponentMax = board.players[int(opponentIdx)].chips
                if incomingBet + board.players[board.activePlayerIndex].chips * BetRatio.LOW_BET > opponentMax:
                    validActions.remove(Action.LOW_BET)
                if incomingBet + board.players[board.activePlayerIndex].chips * BetRatio.MID_BET > opponentMax:
                    validActions.remove(Action.MID_BET)
                if incomingBet + board.players[board.activePlayerIndex].chips * BetRatio.HIGH_BET > opponentMax:
                    validActions.remove(Action.HIGH_BET)
            
            return validActions

    class MCNode:

        def __init__(self, board, parent, isAgent, playerAction):

            # Will be a Board object
            self.board = board

            # parent will be a MCNode object
            self.parent = parent

            # Will contain MCNode objects
            self.children = []

            # NOTE: currently not tracking money won/lost, will add later
            # Win loss ratio info (tie handling undecided)
            self.wins = 0
            self.losses = 0
            self.ties = 0

            # Record the player making the choice
            # Is it the agent or the opponent?
            self.isAgent = isAgent

            # Record the action taken by the player to reach this node
            self.playerAction = playerAction

            # Possible actions the other player can take from this spot
            ## THAT HAVE NOT YET BEEN EXPANDED
            self.availableActions = []
            # DETERMINE BASED OFF OF BOARD STATE
            # Can use a copy of function from round to do this
            self.availableActions = MonteCarloAgent.MCTree.getValidPlayerActions(self.board)

        
    

    def MONTE_CARLO_TREE_SEARCH():
        # TODO: follow pseudocode
        pass





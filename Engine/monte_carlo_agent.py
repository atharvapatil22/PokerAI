from player import Player
from player import Action
from agent import Agent
from deck import Deck
# Get the Board from Round with Round.Board(<constructor arguments>)
from round import Round
import copy

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
            print(len(deck.cards))
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
        #   Choose the action to expand a node for at random, lmao
        def EXPAND(self, leaf):
            # TODO
            pass

        # Run a simulation on the given node
        #   This is where a deck sequence is generated based off of what we know (board variable of node)
        #   Return [amount], where amount is the amount won in the round. (positive is win) (0 is tie (two player game)) (negative is loss)
        def SIMULATE(self, node):
            # TODO
            pass

        # Update the child win/loss/tie stats with the result,
        # and propagate the result to all ancestors of the child (accounting for player change)
        def BACK_PROPAGATE(self, result, child):
            # TODO
            pass

    class MCNode:

        def __init__(self, board, parent, isAgent, playerAction):

            # Will be a Board object
            self.board = board

            # parent will be a MCNode object
            self.parent = parent

            # Will contain MCNode objects
            self.children = []

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
            # TODO: NFNFNF DETERMINE BASED OFF OF BOARD STATE
            # Can use function from round to do this

    
    

    def MONTE_CARLO_TREE_SEARCH():
        # TODO: follow pseudocode
        pass





from player import Player
from player import Action, BetRatio
from agent import Agent
from deck import Deck
# Get the Board from Round with Round.Board(<constructor arguments>)
from round import Round
import copy
from random import randrange
from math import sqrt, log

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

        # Utility of node n
        #   Current implementation: U(n) = n.wins + 0.5 n.ties
        def U(n):
            # TODO: Make this more reflective of actual utility by incorporating chips won
            #       Perhaps U(n) = net money won?
            #       Maybe U(n) = sum(Sqrt(|money won per simulation|) * <-1 if lost money, 1 if gained money>)?
            return n.wins + 0.5*n.ties
        
        # Number of playouts through node n
        #   Current implementation: N(n) = n.wins + n.ties + n.losses
        def N(n):
            return n.wins + n.ties + n.losses
        
        def UCB1(n):
            c = sqrt(2)
            exploitation = MonteCarloAgent.MCTree.U(n) / MonteCarloAgent.MCTree.N(n)
            # If we are operating on the root node, avoid errors by setting exploration to 0
            exploration = 0
            if n.parent is not None:
                exploration = c * sqrt(log(MonteCarloAgent.MCTree.N(n.parent))/MonteCarloAgent.MCTree.N(n))

            return exploitation + exploration


        # Use UCB1 Algorithm to select a leaf node from the tree to expand
        #   Go layer by layer, choose a node from the layer with the highest UCB1 Score
        #   If that node has any remaing actions in availableActions, select that node!
        #   Otherwise, the children of the chosen node become the next "layer".
        #   Repeat until you have a selected node :)
        def selectRecursion(self, layer):
            maxScore = None
            maxIdx = None
            for i in range(layer.__len__()):
                score = MonteCarloAgent.MCTree.UCB1(layer[i])
                if maxScore is None or score > maxScore:
                    maxScore = score
                    maxIdx = i
            chosen = layer[maxIdx]
            if chosen.availableActions.__len__() > 0:
                return chosen
            # IN THIS CASE, THERE ARE NO LEGAL MOVES FOR CHOSEN, MEANING GAME IS AT END STATE
            elif chosen.children.__len__() == 0:
                return chosen
            else:
                return MonteCarloAgent.MCTree.selectRecursion(chosen.children)

        # Use UCB1 Algorithm to select a leaf node from the tree to expand
        #   Go layer by layer, choose a node from the layer with the highest UCB1 Score
        #   If that node has any remaing actions in availableActions, select that node!
        #   Otherwise, the children of the chosen node become the next "layer".
        #   Repeat until you have a selected node :)
        def SELECT(self):
            # Certified recursion classic
            layer = [self.root]
            return MonteCarloAgent.MCTree.selectRecursion(layer)
        
        ### NOTE: STARTING HERE BEGINS THE "handle<Action>" RECREATION STAGE

        # handle functionality when active player places MIN/LOW/MID/HIGH bet 
        # MAKE SURE TO PASS IN A DEEP COPY OF BOARD IF YOU DO NOT WANT TO STAIN BOARD STATE AT PREVIOUS NODE!!!
        def handleBet(board,action):
            incomingBet = board.currentBet - board.playerBets[board.activePlayerIndex]
            # Calculate player bet
            if action == Action.MIN_BET:
                playerBet = incomingBet + board.minBet
            elif action == Action.LOW_BET:
                playerBet = incomingBet + board.players[board.activePlayerIndex].chips * BetRatio.LOW_BET if board.players[board.activePlayerIndex].chips * BetRatio.LOW_BET > board.minBet else board.minBet
            elif action == Action.MID_BET:
                playerBet = incomingBet + board.players[board.activePlayerIndex].chips * BetRatio.MID_BET if board.players[board.activePlayerIndex].chips * BetRatio.MID_BET > board.minBet else board.minBet
            elif action == Action.HIGH_BET:
                playerBet = incomingBet + board.players[board.activePlayerIndex].chips * BetRatio.HIGH_BET if board.players[board.activePlayerIndex].chips * BetRatio.HIGH_BET > board.minBet else board.minBet

            # Update the stored player bet thus far
            board.playerBets[board.activePlayerIndex] += playerBet

            # Update the current bet
            board.currentBet = board.playerBets[board.activePlayerIndex]

            # Player is passing
            board.playersPassing[board.activePlayerIndex] = True
            # Other players must respond to the bet
            for i in range(board.playersPassing.__len__()):
                if i != board.activePlayerIndex:
                    board.playersPassing[i] = False
            
            # print(f"Players passing(IN BET): {self.board.playersPassing}")

            # Update the pot
            board.pot += board.players[board.activePlayerIndex].bet(playerBet)

            # Disable checking if enabled
            if board.checkFlag:
                board.checkFlag = False
                # Not needed after the Phase Change Logic Fix
                # for i in range(self.board.playersPassing.__len__()):
                #     self.board.playersPassing[i] = False
            
        # handle functionality when active player goes all in
        # MAKE SURE TO PASS IN A DEEP COPY OF BOARD IF YOU DO NOT WANT TO STAIN BOARD STATE AT PREVIOUS NODE!!!
        def handleAllIn(board):
            # Calculate player bet
            playerBet = board.players[board.activePlayerIndex].chips

            # Update the stored player bet thus far
            board.playerBets[board.activePlayerIndex] += playerBet

            # Prompt response from other players if the ALL_IN raises the current bet
            promptResponse = False

            # Update the current bet
            if board.playerBets[board.activePlayerIndex] > board.currentBet:
                board.currentBet = board.playerBets[board.activePlayerIndex]
                promptResponse = True

            # Old logic:
            # # Passing if they have 0 chips remaining (have already all-inned)
            # self.board.playersPassing[activePlayerIndex] = False if self.players[activePlayerIndex].chips > 0 else True

            # Player is passing
            board.playersPassing[board.activePlayerIndex] = True
            # If 
            if promptResponse:
                # Other players must respond to the bet
                for i in range(board.playersPassing.__len__()):
                    if i == board.activePlayerIndex:
                        continue
                    elif board.playersAllIn[i]:
                        continue
                    board.playersPassing[i] = False

            # Update the pot
            board.pot += board.players[board.activePlayerIndex].bet(playerBet)

            # Disable checking if enabled
            if board.checkFlag:
                board.checkFlag = False
                # Not needed after the Phase Change Logic Fix
                # for i in range(self.board.playersPassing.__len__()):
                #     self.board.playersPassing[i] = False

            board.playersAllIn[board.activePlayerIndex] = True

        # handle functionality when active player bets opponent max
        # MAKE SURE TO PASS IN A DEEP COPY OF BOARD IF YOU DO NOT WANT TO STAIN BOARD STATE AT PREVIOUS NODE!!!
        def handleOpMax(board):
            incomingBet = board.currentBet - board.playerBets[board.activePlayerIndex]
            # Calculate player bet
            opponentMax = board.players[int((board.activePlayerIndex + 1) % board.players.__len__())].chips
            playerBet = incomingBet + opponentMax

            # Update the stored player bet thus far
            board.playerBets[board.activePlayerIndex] += playerBet

            # Player is passing
            board.playersPassing[board.activePlayerIndex] = True
            # Other players must respond to the bet
            for i in range(board.playersPassing.__len__()):
                if i != board.activePlayerIndex:
                    board.playersPassing[i] = False

            # Update the current bet
            if board.playerBets[board.activePlayerIndex] > board.currentBet:
                board.currentBet = board.playerBets[board.activePlayerIndex]

            # Update the pot
            board.pot += board.players[board.activePlayerIndex].bet(playerBet)

            # Disable checking if enabled
            if board.checkFlag:
                board.checkFlag = False
                # Not needed after the Phase Change Logic Fix
                # for i in range(self.board.playersPassing.__len__()):
                #     self.board.playersPassing[i] = False

            # While not technically "all in", in a two player game, this is sufficient tracking
            board.playersAllIn[board.activePlayerIndex] = True

        # handle functionality when active player calls
        def handleCall(board):
            incomingBet = board.currentBet - board.playerBets[board.activePlayerIndex]
            # Calculate player bet
            playerBet = incomingBet
            # Update the stored player bet thus far
            board.playerBets[board.activePlayerIndex] += playerBet
            # Player is Passing
            board.playersPassing[board.activePlayerIndex] = True
            # Update the pot
            board.pot += board.players[board.activePlayerIndex].bet(playerBet)

        ### NOTE: STARTING HERE ENDS THE "handle<Action>" RECREATION STAGE 

        # Passing Checker Method:
        def phaseChangeCheck(board):
            # Check Condition!
            passing = True

            # If any of the players are not passive, continue this phase
            for j in range(board.playersPassing.__len__()):
                if board.playersPassing[j] == False:
                    passing = False

            # If only one player is not folding or all-in, players are passing manditorily
            activePlayerCount = 0
            for i in range(board.players.__len__()):
                if not board.playersFolding[i] and not board.playersAllIn[i]:
                    activePlayerCount += 1

            # Phases change once every player is folded or passing
            if activePlayerCount <= 1:
                passing = True

            if passing:
                # This means the round/hand is over!
                if board.phase == 4:
                    board.phase += 1
                    return True
                # Otherwise, continue play appropriately
                board.phase += 1
                board.checkFlag = True
                for i in range(board.players.__len__()):
                    if not board.playersFolding[i] and not board.playersAllIn[i]:
                        board.playersPassing[i] = False
                if board.players.__len__() > 2:
                    board.activePlayerIndex = board.buttonPlayerIndex + 1
                else:
                    board.activePlayerIndex = board.buttonPlayerIndex
                

        # Create child node for the selected leaf node based on valid game actions
        #   Choose the action to expand a node for at random
        def EXPAND(self, leaf):
            if leaf.availableActions.__len__() == 0:
                # print("SOMETHING WENT WRONG!")
                # The leaf to return is an end state, just simulate the leaf.
                return leaf
            
            newBoard = copy.deepcopy(leaf.board)

            if newBoard.playersFolding[newBoard.activePlayerIndex] or newBoard.playersAllIn[newBoard.activePlayerIndex]:
                newBoard.playersPassing[newBoard.activePlayerIndex] = True
            else:

                randomActionIdx = randrange(leaf.availableActions.__len__())
                randomAction = leaf.availableActions[randomActionIdx]
                # TODO: Perform the action on newBoard!!!
                # NOTE: This can likely be done by copying some methods from round, making them static, and then using them.
                #       These new static methods should be made in such a way that they can be used in the simulations too!
                
                # Handle player action
                if randomAction in [Action.MIN_BET,Action.LOW_BET,Action.MID_BET,Action.HIGH_BET]:
                    self.handleBet(newBoard,randomAction)
                elif randomAction == Action.ALL_IN:
                    self.handleAllIn(newBoard)
                elif randomAction == Action.OP_MAX:
                    self.handleOpMax(newBoard)
                elif randomAction == Action.CALL:
                    self.handleCall(newBoard)
                elif randomAction == Action.CHECK:
                    # Passing
                    newBoard.playersPassing[newBoard.activePlayerIndex] = True
                elif randomAction == Action.FOLD:
                    # Folded
                    newBoard.playersFolding[newBoard.activePlayerIndex] = True
                    # Passing
                    newBoard.playersPassing[newBoard.activePlayerIndex] = True

            # After accounting for the applied action, it is now the next player's turn
            newBoard.activePlayerIndex += 1
            newBoard.activePlayerIndex = (newBoard.activePlayerIndex) % newBoard.players.__len__()
            
            # This method will return True if an end state is reached, but in terms of creating new nodes,
            # we kind of don't care. That is just there so the method can be used in simulations
            MonteCarloAgent.MCTree.phaseChangeCheck(newBoard)

            newChild = MonteCarloAgent.MCNode(newBoard, leaf, not leaf.isAgent, leaf.availableActions.pop(randomActionIdx))

            leaf.children.append(newChild)
            
            return newChild

        # Run a simulation on the given node
        #   This is where a deck sequence is generated based off of what we know (board variable of node)
        #   Return [amount], where amount is the amount won in the round. (positive is win) (0 is tie (two player game)) (negative is loss)
        def SIMULATE(self, node):
            # TODO
            # NOTE: At the start of each simulation, simulate a new set of unknown cards.
            #       This means that "newly revealed" community cards will not be stored in nodes of "future"
            #       phases, if the "real" game state does not have those cards revealed.
            #       This means that the nodes with "future" phases will not have new community cards,
            #       and it will be the job of the simulator to know how many cards to simulate and reveal at
            #       the time of simulation. (phase 1-->0 CC, 2-->3 CC, 3-->4 CC, 4-->5 CC)
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
                self.BACK_PROPAGATE(-result, simNode.parent)
            pass

        # This is a Static version of a function from round.py
        # Function will determine all the valid actions for the active player
        def getValidPlayerActions(self, board):
            # Copy all the player actions
            validActions = [member for _, member in Action.__members__.items()]

            # The round/hand is over, scoring should now commence!!!
            if board.phase == 5:
                return []

            # If a player has already gone all in, they have no other choice
            if board.playersAllIn[board.activePlayerIndex]:
                return [Action.ALL_IN]
            # If a player folds at any point in time, they cannot un-fold
            elif board.playersFolding[board.activePlayerIndex]:
                return [Action.FOLD]

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

            # Record the player who made the choice that resulted in this node
            # Is it the agent or the opponent?
            # NOTE: As the person who initially wrote this code, I'm not sure what this is doing, or if it is doing anything.
            self.isAgent = isAgent

            # Record the action taken by the player to reach this node
            self.playerAction = playerAction

            # Possible actions the other player can take from this spot
            ## THAT HAVE NOT YET BEEN EXPANDED
            self.availableActions = []
            # DETERMINE BASED OFF OF BOARD STATE
            # Can use a copy of function from round to do this
            self.availableActions = MonteCarloAgent.MCTree.getValidPlayerActions(self.board)
            # # Remove FOLD option, it should not occur in tree????
            # self.availableActions.remove(Action.FOLD)

        
    

    def MONTE_CARLO_TREE_SEARCH(self, board, numSim):
        # TODO: follow pseudocode
        tree = MonteCarloAgent.MCTree(board)
        for i in range(numSim):
            leaf = tree.SELECT()
            child = tree.EXPAND(leaf)
            # NOTE: SIMULATE has not been implemented
            result = tree.SIMULATE(child)
            tree.BACK_PROPAGATE(result, child)

        maxNumPlayouts = None
        chosenNode = None
        for i in range(tree.root.children.__len__()):
            node = tree.root.children[i]
            numPlayouts = MonteCarloAgent.MCTree.N(node)
            if maxNumPlayouts is None or numPlayouts > maxNumPlayouts or (numPlayouts == maxNumPlayouts and MonteCarloAgent.MCTree.U(node) > MonteCarloAgent.MCTree.U(chosenNode)):
                maxNumPlayouts = numPlayouts
                chosenNode = node
        chosenAction = chosenNode.playerAction
        return chosenAction






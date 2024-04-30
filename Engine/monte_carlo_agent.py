from card import Card
from player import Player
from player import Action, BetRatio
from agent import Agent
from deck import Deck
# Get the Board from Round with Round.Board(<constructor arguments>)
from round import Round
import copy
from random import randrange
from math import sqrt, log, ceil

class MonteCarloAgent(Agent):

    def get_action(self, board, validActions):
        # Store the record of each player in the existing player objects, clear them, make copies, then restore them.
        #   This is done to ensure that the record is not modified in the new board.
        playerRecords = []
        for i in range(board.players.__len__()):
            playerRecords.append(board.players[i].chipRecord)
            board.players[i].chipRecord = []
        
        
        action = self.MONTE_CARLO_TREE_SEARCH(board, 100)
        # print(f"Monte Carlo Agent chose: {action}")

        for i in range(board.players.__len__()):
            board.players[i].chipRecord = playerRecords[i]

        return action
    
    class MCTree:

        def __init__(self, boardState):

            self.root = MonteCarloAgent.MCNode(boardState, None, False, None)
            self.agentIndex = copy.deepcopy(boardState.activePlayerIndex)
            #NFNF

        # Utility of node n
        #   Current implementation: U(n) = n.wins + 0.5 n.ties
        def U(n):
            # TODO: Make this more reflective of actual utility by incorporating chips won
            #       Perhaps U(n) = net money won?
            #       Maybe U(n) = sum(Sqrt(|money won per simulation|) * <-1 if lost money, 1 if gained money>)?
            # return n.wins + 0.5*n.ties
            # return n.chipsWon
            # return n.chipsWon / n.wins
            return n.chipsWonSqrt

        
        
        # Number of playouts through node n
        #   Current implementation: N(n) = n.wins + n.ties + n.losses
        def N(n):
            return n.wins + n.ties + n.losses
        
        def UCB1(n):
            # c = sqrt(2)
            c = sqrt(2) * 2
            # if (n.wins + 0.5* n.ties) != 0:
            #     c *= MonteCarloAgent.MCTree.U(n)/(n.wins + 0.5 * n.ties)
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
            if layer.__len__() == 1:
                chosen = layer[0]
            else:
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
                return MonteCarloAgent.MCTree.selectRecursion(self, chosen.children)

        # Use UCB1 Algorithm to select a leaf node from the tree to expand
        #   Go layer by layer, choose a node from the layer with the highest UCB1 Score
        #   If that node has any remaing actions in availableActions, select that node!
        #   Otherwise, the children of the chosen node become the next "layer".
        #   Repeat until you have a selected node :)
        def SELECT(self):
            # Certified recursion classic
            layer = [self.root]
            return MonteCarloAgent.MCTree.selectRecursion(self, layer)
        
        ### NOTE: STARTING HERE BEGINS THE "handle<Action>" RECREATION STAGE

        # handle functionality when active player places MIN/LOW/MID/HIGH bet 
        # MAKE SURE TO PASS IN A DEEP COPY OF BOARD IF YOU DO NOT WANT TO STAIN BOARD STATE AT PREVIOUS NODE!!!
        def handleBet(self, board,action):
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
                if i == board.activePlayerIndex:
                    continue
                elif board.playersAllIn[i]:
                    continue
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
        def handleAllIn(self, board):
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
                
                # Disable checking if enabled
                if board.checkFlag:
                    board.checkFlag = False

                for i in range(board.playersPassing.__len__()):
                    if i == board.activePlayerIndex:
                        continue
                    elif board.playersAllIn[i]:
                        continue
                    board.playersPassing[i] = False
            # print("players passing inside", board.playersPassing)
            # print("players all in", board.playersAllIn)
            # print("active player index", board.activePlayerIndex)
            # Update the pot
            board.pot += board.players[board.activePlayerIndex].bet(playerBet)

            

            board.playersAllIn[board.activePlayerIndex] = True

        # handle functionality when active player bets opponent max
        # MAKE SURE TO PASS IN A DEEP COPY OF BOARD IF YOU DO NOT WANT TO STAIN BOARD STATE AT PREVIOUS NODE!!!
        def handleOpMax(self, board):
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
                if i == board.activePlayerIndex:
                    continue
                elif board.playersAllIn[i]:
                    continue
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
        def handleCall(self, board):
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
                return True
            else:
                return False
                

        # Create child node for the selected leaf node based on valid game actions
        #   Choose the action to expand a node for at random
        def EXPAND(self, leaf):
            if leaf.availableActions.__len__() == 0:
                # print("SOMETHING WENT WRONG!")
                # The leaf to return is an end state, just simulate the leaf.
                return leaf

            newBoard = copy.deepcopy(leaf.board)

            randomActionIdx = -1
            if newBoard.playersFolding[newBoard.activePlayerIndex] or newBoard.playersAllIn[newBoard.activePlayerIndex]:
                newBoard.playersPassing[newBoard.activePlayerIndex] = True
            else:

                suggestedAction = MonteCarloAgent.MCTree.getPlayoutPolicyActionSimpleProbability(self, newBoard, leaf.availableActions)
                if suggestedAction in leaf.availableActions:
                    randomActionIdx = leaf.availableActions.index(suggestedAction)
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
            
            # This method will return True if phase is changed, repeat until it returns false,
            # or if the phase is 5 (end state)
            phaseChange = True
            while phaseChange:
                phaseChange = MonteCarloAgent.MCTree.phaseChangeCheck(newBoard)
                if newBoard.phase == 5:
                    phaseChange = False

            newChild = MonteCarloAgent.MCNode(newBoard, leaf, not leaf.isAgent, leaf.availableActions.pop(randomActionIdx))

            leaf.children.append(newChild)
            
            return newChild
        
        def endTurn(board): # Check if the phase should change (all players are passive)
            # If any of the players are not passive, continue this phase
            for j in range(board.playersPassing.__len__()):
                if board.playersPassing[j] == False:
                    return False

            # Increment the phase and reset the board
            board.phase += 1
            for i in range(board.players.__len__()):
                board.playersPassing[i] = False
                board.playersFolding[i] = False
                board.playersAllIn[i] = False
            return True

        def SIMULATE(self, node):
            simulatedBoard = copy.deepcopy(node.board)

            opponentIdx = (self.agentIndex + 1) % simulatedBoard.players.__len__()
            # The index of the player who made the choice can be derived from the isAgent field
            #   The index of the player who made the choice, is the player BEFORE the active player
            simulatedIndex = self.agentIndex if node.isAgent else opponentIdx

            # copy.deepcopy((simulatedBoard.activePlayerIndex + 1) % simulatedBoard.players.__len__())

            #create newly randomized deck
            randDeck = Deck(True, None)
            #remove cards that are in the agent's hand and community
            removeCards = simulatedBoard.players[self.agentIndex].cardsInHand + self.root.board.community
            #remove cards that are in the agent's hand and community
            for cardToRemove in removeCards:
                for card in randDeck.cards:
                    if card.id == cardToRemove.id:
                        randDeck.cards.remove(card)
                        break
            
            simulatedBoard.players[opponentIdx].cardsInHand = [randDeck.top(), randDeck.top()]

            simPhaseDiff = simulatedBoard.phase - self.root.board.phase #see if board is not in same phase as real game
            if simPhaseDiff > 0: #if simulation is not synced, fill in community cards
                # print("Simulating phase difference")    
                if simulatedBoard.community.__len__() == 0 and simulatedBoard.phase >= 2: #if past phase 1 and no community cards, add them
                    for _ in range(3):
                        # print("Added 3 community card")
                        simulatedBoard.community.append(randDeck.top())
                if simulatedBoard.community.__len__() == 3 and simulatedBoard.phase >= 3: #if past phase 2 and only 3 community cards, add them
                    simulatedBoard.community.append(randDeck.top())
                if simulatedBoard.phase >= 4: # if phase 4 or 5, add last community card
                    # print("Added community card")
                    simulatedBoard.community.append(randDeck.top())
                    # print("Community length: " + str(len(community)))
            
            # Setup complete, ready to begin
            while simulatedBoard.phase < 5:
                # Alternate turns, similar logic to round.py

                # Active player takes a turn
                # Get the action
                # Random Action
                
                ourChips = simulatedBoard.players[simulatedBoard.activePlayerIndex].chips
                
                availableSimActions = MonteCarloAgent.MCTree.getValidPlayerActions(self, simulatedBoard)
                # action = MonteCarloAgent.MCTree.getPlayoutPolicyActionSimulation(self, simulatedBoard, availableSimActions)
                # action = MonteCarloAgent.MCTree.getPlayoutPolicyActionSimple(self, simulatedBoard, availableSimActions)
                # action = MonteCarloAgent.MCTree.getPlayoutPolicyActionSimpleProbability(self, simulatedBoard, availableSimActions)
                # action = MonteCarloAgent.MCTree.getPlayoutPolicyActionSimpAdj(self, simulatedBoard, availableSimActions)
                
                # get random action
                randomActionIdx = randrange(availableSimActions.__len__())
                action = availableSimActions[randomActionIdx]
                opponentChips = simulatedBoard.players[simulatedBoard.activePlayerIndex].chips
                if (action == Action.LOW_BET and opponentChips < ourChips * BetRatio.LOW_BET or 
                    action == Action.MID_BET and opponentChips < ourChips * BetRatio.MID_BET or 
                    action == Action.HIGH_BET and opponentChips < ourChips * BetRatio.HIGH_BET or
                    action == Action.ALL_IN and opponentChips < ourChips):
                    action = Action.OP_MAX

                # randomActionIdx = randrange(availableSimActions.__len__())
                # randomAction = availableSimActions[randomActionIdx]
                randomAction = action
                # Handle the action
                # Handle player action
                if randomAction in [Action.MIN_BET,Action.LOW_BET,Action.MID_BET,Action.HIGH_BET]:
                    self.handleBet(simulatedBoard,randomAction)
                elif randomAction == Action.ALL_IN:
                    self.handleAllIn(simulatedBoard)
                elif randomAction == Action.OP_MAX:
                    self.handleOpMax(simulatedBoard)
                elif randomAction == Action.CALL:
                    self.handleCall(simulatedBoard)
                elif randomAction == Action.CHECK:
                    # Passing
                    simulatedBoard.playersPassing[simulatedBoard.activePlayerIndex] = True
                elif randomAction == Action.FOLD:
                    # Folded
                    simulatedBoard.playersFolding[simulatedBoard.activePlayerIndex] = True
                    # Passing
                    simulatedBoard.playersPassing[simulatedBoard.activePlayerIndex] = True

                # After accounting for the applied action, it is now the next player's turn
                # Increment turn
                simulatedBoard.activePlayerIndex += 1
                # Handle overflow
                simulatedBoard.activePlayerIndex = (simulatedBoard.activePlayerIndex) % simulatedBoard.players.__len__()
                
                # Recursive phaseChangeCheck call
                #   Within the loop, update the community cards as necessary
                #   Make sure to set the activePlayerIndex appropriately
                phaseChange = True
                while phaseChange:
                    phaseChange = MonteCarloAgent.MCTree.phaseChangeCheck(simulatedBoard)
                    # Handle phase change if necessary
                    if phaseChange:
                        # allow for checking at the beginning of each phase
                        simulatedBoard.checkFlag = True
                        # participating players are no longer passive
                        for i in range(simulatedBoard.players.__len__()):
                            if not simulatedBoard.playersFolding[i]:
                                simulatedBoard.playersPassing[i] = False
                        # handle who goes first after phase change
                        if simulatedBoard.players.__len__() > 2:
                            simulatedBoard.activePlayerIndex = simulatedBoard.buttonPlayerIndex + 1
                        else:
                            simulatedBoard.activePlayerIndex = simulatedBoard.buttonPlayerIndex

                        # Handle community card update
                        # Phase 1-->2 Preflop --> Flop
                        if simulatedBoard.phase == 2:
                        # if self.board.phase == 1:
                            simulatedBoard.community.append(randDeck.top())
                            simulatedBoard.community.append(randDeck.top())
                            simulatedBoard.community.append(randDeck.top())
                        # Phase 2-->3 Flop --> Turn
                        # Phase 3-->4 Turn --> River
                        elif simulatedBoard.phase == 3 or simulatedBoard.phase == 4:
                        # elif self.board.phase == 2 or self.board.phase == 3:
                            simulatedBoard.community.append(randDeck.top())
                        # Phase 4-->5 River --> Scores
                        elif simulatedBoard.phase == 5:
                            break
            

            # Scoring time
            scores = []
            for i in range(simulatedBoard.players.__len__()):
                # Folding players get 0 points
                if simulatedBoard.playersFolding[i]:
                    scores.append(0)
                # Scores are calculated by the player objects
                else:
                    # REFNOTE: This could change to being done by the Engine, taking
                    # each players 2 card hand and the community cards into account 
                    hand = simulatedBoard.players[i].cardsInHand + simulatedBoard.community
                    scores.append(MonteCarloAgent.handScore(hand))
            # Find winners
            maxScore = -1
            winningIndex = []
            for i in range(simulatedBoard.players.__len__()):
                if scores[i] > maxScore:
                    maxScore = scores[i]
                    winningIndex = [i]
                # There can be multiple Players with equal strength best hands
                elif scores[i] == maxScore:
                    winningIndex.append(i)
            
            if winningIndex.__len__() > 1:
                # Tie
                return 0
            elif winningIndex[0] == simulatedIndex:
                # Player who made choice resulting in node, won
                return (simulatedBoard.pot - simulatedBoard.playerBets[winningIndex[0]])
            else:
                losing_index = (winningIndex[0] + 1) % 2
                # Player who made choice resulting in node, lost
                return -(simulatedBoard.playerBets[losing_index])

        # Update the child win/loss/tie stats with the result,
        # and propagate the result to all ancestors of the child(simNode) (accounting for player change)
        def BACK_PROPAGATE(self, result, simNode):
            # TODO: Make the result propagate as well, storing amount of money won/lost
            # NOTE: The above TODO relies on functionality in the MCNode class that does not yet exist
            # print("Result: " + str(result))
            
            if result > 0:
                simNode.wins += 1
                simNode.chipsWon += result
                simNode.chipsWonSqrt += sqrt(result)
            elif result < 0:
                simNode.losses += 1
                simNode.chipsWon += result
                simNode.chipsWonSqrt -= sqrt(abs(result))
            else:
                simNode.ties += 1
                simNode.chipsWon += result
                simNode.chipsWonSqrt -= sqrt(abs(result))

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
            if board.players[int(opponentIdx)].chips == 0:
                # Opponent is already all in
                validActions.remove(Action.OP_MAX)
                if Action.MIN_BET in validActions:
                    validActions.remove(Action.MIN_BET)
                if Action.MID_BET in validActions:
                    validActions.remove(Action.MID_BET)
                if Action.HIGH_BET in validActions:
                    validActions.remove(Action.HIGH_BET)
            if board.players[int(opponentIdx)].chips + incomingBet >= board.players[int(board.activePlayerIndex)].chips:
                # Not enough chips to overbet other player
                if Action.OP_MAX in validActions:
                    validActions.remove(Action.OP_MAX)
            else:
                # These actions would now overbet the opponent max
                validActions.remove(Action.ALL_IN)
                opponentMax = board.players[int(opponentIdx)].chips
                if incomingBet + board.players[board.activePlayerIndex].chips * BetRatio.LOW_BET > opponentMax:
                    if Action.LOW_BET in validActions:
                        validActions.remove(Action.LOW_BET)
                if incomingBet + board.players[board.activePlayerIndex].chips * BetRatio.MID_BET > opponentMax:
                    if Action.MID_BET in validActions:
                        validActions.remove(Action.MID_BET)
                if incomingBet + board.players[board.activePlayerIndex].chips * BetRatio.HIGH_BET > opponentMax:
                    if Action.HIGH_BET in validActions:
                        validActions.remove(Action.HIGH_BET)
            
            return validActions
        

        # This can either be 30 full simulations to determine winrate against the opponent (add in commented lines)
        # OR do 5 simulations of your hand to get an average hand score (current implementation)
        def getPlayoutPolicyActionSimulation(self, board, validActions):
            cards_in_hand = board.players[board.activePlayerIndex].cardsInHand # Player current cards
            community_cards = self.root.board.community # Current community cards
            cards_to_remove = cards_in_hand + community_cards # Cards we don't want in the deck so we don't get them twice
            # your_wins = 0
            # opponent_wins = 0
            # ties = 0
            simulations = 5
            total_hand_score = 0
            deck = Deck(True, None)
            for card_to_remove in cards_to_remove: # Remove cards we don't want to get twice from the deck
                for card in deck.cards:
                    if card.id == card_to_remove.id:
                        deck.cards.remove(card)
                        break
            original_cards = deck.cards # Keep a copy of the cards to use for every simulation to save runtime
            for _ in range(simulations):
                deck.cards = original_cards.copy()
                # print(len(deck.cards))
                # opponent_hand = [deck.top(), deck.top()] + community_cards
                hand = cards_in_hand + community_cards
                randomized_community_cards = []
                for _ in range(5-len(community_cards)):
                    randomized_community_cards.append(deck.top()) # Randomize the rest of the community cards to reach 5
                # opponent_hand += randomized_community_cards
                hand += randomized_community_cards
                hand_score = MonteCarloAgent.handScore(hand) # Score the hand for this simulation
                total_hand_score += hand_score # Increment the total
                # opponent_score = MonteCarloAgent.handScore(opponent_hand)
                # if hand_score > opponent_score:
                #     your_wins +=1
                # elif hand_score == opponent_score:
                #     ties +=1
                # else:
                #     opponent_wins +=1
            # your_win_percentage = (your_wins+0.5*ties)/(simulations)
            import random as rnd
            random_number = rnd.random()
            average_hand_score = total_hand_score/simulations # Get the average hand score based on the simulations and act accordingly
            # print("Average hand score: ", average_hand_score)
            # print("Average hand score: ", average_hand_score)
            if(average_hand_score > 250): # If you have a very good hand, be very aggressive
            # if(your_win_percentage > 0.6):
                if(random_number < 0.3): # some randomness, 30% chance of being passive with a good hand
                    if(Action.CHECK in validActions):
                        return Action.CHECK
                    elif(Action.CALL in validActions):
                        return Action.CALL
                    return Action.ALL_IN
                if(Action.MID_BET in validActions):
                    random2 = rnd.random()
                    if(Action.HIGH_BET in validActions and random2 < 0.5): # 50/50 on high or mid bet
                        return Action.HIGH_BET
                    return Action.MID_BET
                else: # If you can't mid or high bet, must max out opponent or all in
                    if(Action.OP_MAX in validActions):
                        return Action.OP_MAX
                    return Action.ALL_IN
            if(average_hand_score > 215): # If a fairly good hand, be slightly aggressive
            # if(your_win_percentage > 0.5):
                if(random_number < 0.3): # some randomness, 30% chance of being passive with a good hand
                    if(Action.CHECK in validActions):
                        return Action.CHECK
                    elif(Action.CALL in validActions):
                        return Action.CALL
                    return Action.ALL_IN
                if(Action.MIN_BET in validActions):
                    random2 = rnd.random()
                    if(Action.LOW_BET in validActions and random2 < 0.5): # 50/50 on low or min bet
                        return Action.LOW_BET
                    return Action.MIN_BET
                else: # If you can't mid or high bet, must max out opponent or all in
                    if(Action.OP_MAX in validActions):
                        return Action.OP_MAX
                    return Action.ALL_IN
            elif(average_hand_score > 180): # If an okay hand, be passive
            # elif(your_win_percentage > 0.4):
                if(random_number < 0.3): # some randomness, 30% chance of being aggressive with an okay hand
                    if(Action.MID_BET in validActions):
                        random2 = rnd.random()
                        if(Action.HIGH_BET in validActions and random2 < 0.5): # 50/50 on high or mid bet
                            return Action.HIGH_BET
                        return Action.MID_BET
                    else:
                        return Action.ALL_IN
                if(Action.CHECK in validActions):
                    return Action.CHECK
                elif(Action.CALL in validActions):
                    return Action.CALL
                return Action.ALL_IN
            else: # bad hand
                return Action.FOLD

        # Create a dictionary for every off suit pair of cards, and a rank of the hand
        OFF_SUIT = {(2,2):7,(2,3):10,(2,4):10,(2,5):10,(2,6):10,(2,7):10,(2,8):10,(2,9):10,(2,10):10,(2,11):10,(2,12):10,(2,13):10,(2,14):10,
                    (3,3):7,(3,4):10,(3,5):10,(3,6):10,(3,7):10,(3,8):10,(3,9):10,(3,10):10,(3,11):10,(3,12):10,(3,13):10,(3,14):10,
                    (4,4):7,(4,5):8,(4,6):10,(4,7):10,(4,8):10,(4,9):10,(4,10):10,(4,11):10,(4,12):10,(4,13):10,(4,14):10,
                    (5,5):6,(5,6):8,(5,7):10,(5,8):10,(5,9):10,(5,10):10,(5,11):10,(5,12):10,(5,13):10,(5,14):10,
                    (6,6):6,(6,7):8,(6,8):10,(6,9):10,(6,10):10,(6,11):10,(6,12):10,(6,13):10,(6,14):10,
                    (7,7):5,(7,8):8,(7,9):10,(7,10):10,(7,11):10,(7,12):10,(7,13):10,(7,14):10,
                    (8,8):4,(8,9):7,(8,10):8,(8,11):8,(8,12):10,(8,13):10,(8,14):10,
                    (9,9):3,(9,10):7,(9,11):7,(9,12):8,(9,13):8,(9,14):8,
                    (10,10):2,(10,11):5,(10,12):6,(10,13):6,(10,14):6,
                    (11,11):1,(11,12):5,(11,13):5,(11,14):4,
                    (12,12):1,(12,13):4,(12,14):3,
                    (13,13):1,(13,14):2,
                    (14,14):1}
        ON_SUIT = {(2,3):8,(2,4):8,(2,5):9,(2,6):9,(2,7):9,(2,8):9,(2,9):9,(2,10):9,(2,11):9,(2,12):9,(2,13):7,(2,14):5,
                    (3,4):7,(3,5):7,(3,6):9,(3,7):9,(3,8):9,(3,9):9,(3,10):9,(3,11):9,(3,12):9,(3,13):7,(3,14):5,
                    (4,5):6,(4,6):7,(4,7):8,(4,8):9,(4,9):9,(4,10):9,(4,11):9,(4,12):9,(4,13):7,(4,14):5,
                    (5,6):7,(5,7):6,(5,8):8,(5,9):9,(5,10):9,(5,11):9,(5,12):9,(5,13):7,(5,14):5,
                    (6,7):5,(6,8):6,(6,9):8,(6,10):9,(6,11):9,(6,12):9,(6,13):7,(6,14):5,
                    (7,8):5,(7,9):5,(7,10):7,(7,11):8,(7,12):9,(7,13):7,(7,14):5,
                    (8,9):4,(8,10):5,(8,11):6,(8,12):7,(8,13):7,(8,14):5,
                    (9,10):4,(9,11):4,(9,12):5,(9,13):6,(9,14):5,
                    (10,11):3,(10,12):4,(10,13):4,(10,14):3,
                    (11,12):3,(11,13):3,(11,14):2,
                    (12,13):2,(12,14):2,
                    (13,14):1}
                   
        def getPlayoutPolicyActionSimple(self, board, validActions):
            cards_in_hand = board.players[board.activePlayerIndex].cardsInHand
            community_cards = self.root.board.community
            incomingBet = board.currentBet - board.playerBets[board.activePlayerIndex]
            playerChips = board.players[board.activePlayerIndex].chips
            playerBet = board.playerBets[board.activePlayerIndex]
            playerTotal = playerChips + playerBet
            modifier = 0 
            if incomingBet >= playerTotal: # maybe able to remove this one
                modifier = 5
            elif incomingBet >= playerTotal * BetRatio.HIGH_BET:
                modifier = 4
            elif incomingBet >= playerTotal * BetRatio.MID_BET:
                modifier = 3
            elif incomingBet >= playerTotal * BetRatio.LOW_BET:
                modifier = 2
            elif incomingBet == board.minBet: 
                modifier = 1
            else:
                modifier = 0

            policyRank = -1
            # No community cards are present (hole cards only)
            if community_cards.__len__() == 0:
                sameSuit = True if cards_in_hand[0].suit == cards_in_hand[1].suit else False
                # valKey as a tuple of the two card values, sorted
                valKey = tuple(sorted([cards_in_hand[0].value, cards_in_hand[1].value]))
                handRank = self.OFF_SUIT[valKey] if not sameSuit else self.ON_SUIT[valKey]
                policyRank = handRank - modifier
                
            # Some community cards are present      
            else:
                handScore = MonteCarloAgent.handScore(cards_in_hand + community_cards)
                handRank = 11 - ceil(handScore / 100)
                policyRank = handRank - modifier - 4
                if policyRank < 1:
                    policyRank = 1

             # Make the player act probibilistically according to how strong their hand is and the modifier
            if policyRank == 1:
                return Action.ALL_IN
                
            elif policyRank == 2:
                if Action.HIGH_BET in validActions:
                    return Action.HIGH_BET
                elif Action.OP_MAX in validActions:
                    return Action.OP_MAX
                elif Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.ALL_IN
                    
            elif policyRank == 3:
                if Action.MID_BET in validActions:
                    return Action.MID_BET
                elif Action.OP_MAX in validActions:
                    return Action.OP_MAX
                elif Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.ALL_IN
                    
            elif policyRank == 4:
                if Action.LOW_BET in validActions:
                    return Action.LOW_BET
                elif Action.OP_MAX in validActions:
                    return Action.OP_MAX
                elif Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.ALL_IN
                    
            elif policyRank == 5:
                if Action.LOW_BET in validActions:
                    return Action.LOW_BET
                elif Action.OP_MAX in validActions:
                    return Action.OP_MAX
                elif Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.FOLD
                    
            elif policyRank == 6:
                if Action.MIN_BET in validActions:
                    return Action.MIN_BET
                elif Action.OP_MAX in validActions:
                    return Action.OP_MAX
                elif Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.FOLD
                    
            elif policyRank == 7:
                if Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.FOLD
                    
            elif policyRank == 8:
                if Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.FOLD
                
            elif policyRank == 9:
                return Action.FOLD
                    
            elif policyRank == 10:
                return Action.FOLD
                    
            else:
                return Action.FOLD
            
        def getPlayoutPolicyActionSimpAdj(self, board, validActions):
            cards_in_hand = board.players[board.activePlayerIndex].cardsInHand
            community_cards = self.root.board.community
            incomingBet = board.currentBet - board.playerBets[board.activePlayerIndex]
            playerChips = board.players[board.activePlayerIndex].chips
            playerBet = board.playerBets[board.activePlayerIndex]
            playerTotal = playerChips + playerBet
            modifier = 0 
            if incomingBet >= playerTotal: # maybe able to remove this one
                modifier = 5
            elif incomingBet >= playerTotal * BetRatio.HIGH_BET:
                modifier = 4
            elif incomingBet >= playerTotal * BetRatio.MID_BET:
                modifier = 3
            elif incomingBet >= playerTotal * BetRatio.LOW_BET:
                modifier = 2
            elif incomingBet == board.minBet: 
                modifier = 1
            else:
                modifier = 0

            policyRank = -1
            # No community cards are present (hole cards only)
            if community_cards.__len__() == 0:
                sameSuit = True if cards_in_hand[0].suit == cards_in_hand[1].suit else False
                # valKey as a tuple of the two card values, sorted
                valKey = tuple(sorted([cards_in_hand[0].value, cards_in_hand[1].value]))
                handRank = self.OFF_SUIT[valKey] if not sameSuit else self.ON_SUIT[valKey]
                policyRank = handRank - modifier
                
            # Some community cards are present      
            else:
                handScore = MonteCarloAgent.handScore(cards_in_hand + community_cards)
                handRank = 11 - ceil(handScore / 100)
                policyRank = handRank - modifier - 4
                if policyRank < 1:
                    policyRank = 1

             # Make the player act probibilistically according to how strong their hand is and the modifier
            if policyRank == 1 or policyRank == 2:
                return Action.ALL_IN
                    
            elif policyRank == 3:
                if Action.HIGH_BET in validActions:
                    return Action.HIGH_BET
                elif Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.ALL_IN
                    
            elif policyRank == 4:
                if Action.MID_BET in validActions:
                    return Action.MID_BET
                elif Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.ALL_IN
                    
            elif policyRank == 5:
                if Action.LOW_BET in validActions:
                    return Action.LOW_BET
                elif Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.FOLD
                    
            elif policyRank == 6:
                if Action.MIN_BET in validActions:
                    return Action.MIN_BET
                elif Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.FOLD
                    
            elif policyRank == 7:
                if Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.FOLD
                    
            elif policyRank == 8:
                if Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.FOLD
                
            elif policyRank == 9:
                return Action.FOLD
                    
            elif policyRank == 10:
                return Action.FOLD
                    
            else:
                return Action.FOLD




        def getPlayoutPolicyActionSimpleProbability(self, board, validActions):
            cards_in_hand = board.players[board.activePlayerIndex].cardsInHand
            community_cards = self.root.board.community
            incomingBet = board.currentBet - board.playerBets[board.activePlayerIndex]
            # opponentAllIn = True if board.players[(board.activePlayerIndex + 1) % board.players.__len__()].chips == 0 else False
            playerChips = board.players[board.activePlayerIndex].chips
            playerBet = board.playerBets[board.activePlayerIndex]
            playerTotal = playerChips + playerBet
            modifier = 0 
            if incomingBet >= playerTotal: # maybe able to remove this one
                modifier = 5
            elif incomingBet >= playerTotal * BetRatio.HIGH_BET:
                modifier = 4
            elif incomingBet >= playerTotal * BetRatio.MID_BET:
                modifier = 3
            elif incomingBet >= playerTotal * BetRatio.LOW_BET:
                modifier = 2
            elif incomingBet == board.minBet: 
                modifier = 1
            else:
                modifier = 0

            policyRank = -1
            # No community cards are present (hole cards only)
            if community_cards.__len__() == 0:
                sameSuit = True if cards_in_hand[0].suit == cards_in_hand[1].suit else False
                # valKey as a tuple of the two card values, sorted
                valKey = tuple(sorted([cards_in_hand[0].value, cards_in_hand[1].value]))
                handRank = self.OFF_SUIT[valKey] if not sameSuit else self.ON_SUIT[valKey]
                policyRank = handRank - modifier
                
            # Some community cards are present      
            else:
                # Simulate the remaining commnity cards n times
                # Take the average of the resulting hand scores
                # convert to a rank, and then apply the modifier
                # n = 1
                # handScores = []
                # for _ in range(n):
                #     deck = Deck(True, None)
                #     for card_to_remove in cards_in_hand:
                #         for card in deck.cards:
                #             if card.id == card_to_remove.id:
                #                 deck.cards.remove(card)
                #                 break
                #     for card_to_remove in community_cards:
                #         for card in deck.cards:
                #             if card.id == card_to_remove.id:
                #                 deck.cards.remove(card)
                #                 break
                #     randomized_community_cards = []
                #     for _ in range(5-len(community_cards)):
                #         randomized_community_cards.append(deck.top())
                #     hand = cards_in_hand + community_cards + randomized_community_cards
                #     handScores.append(MonteCarloAgent.handScore(hand))
                # # compute the average hand score
                # avgHandScore = sum(handScores) / n
                # # convert to a rank: 11 - (average divided by 100 and round up)
                # handRank = 11 - ceil(avgHandScore / 100)
                handScore = MonteCarloAgent.handScore(cards_in_hand + community_cards)
                handRank = 11 - ceil(handScore / 100)
                policyRank = handRank - modifier - 4
                if policyRank < 1:
                    policyRank = 1


            # Make the player act probibilistically according to how strong their hand is and the modifier
            if policyRank == 1:
                # One of the best hands
                # 5% all in, 20% high bet, 30% mid bet, 40% low bet, 0% min bet, 5% call/check, 0% fold
                randNum = randrange(1,100)
                if randNum <= 5:
                    if Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    elif Action.ALL_IN in validActions:
                        return Action.ALL_IN
                elif randNum <= 25:
                    if Action.HIGH_BET in validActions:
                        return Action.HIGH_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                elif randNum <= 55:
                    if Action.MID_BET in validActions:
                        return Action.MID_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                elif randNum <= 95:
                    if Action.LOW_BET in validActions:
                        return Action.LOW_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                if randNum > 95:
                    if Action.CALL in validActions:
                        return Action.CALL
                    elif Action.CHECK in validActions:
                        return Action.CHECK
                    else:
                        return Action.ALL_IN
                
            elif policyRank == 2:
                # Very strong hand
                # 5% all in, 5% high bet, 30% mid bet, 40% low bet, 15% min bet, 5% call/check, 0% fold
                randNum = randrange(1,100)
                if randNum <= 5:
                    if Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    elif Action.ALL_IN in validActions:
                        return Action.ALL_IN
                if randNum <= 10:
                    if Action.HIGH_BET in validActions:
                        return Action.HIGH_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                if randNum <= 40:
                    if Action.MID_BET in validActions:
                        return Action.MID_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                if randNum <= 80:
                    if Action.LOW_BET in validActions:
                        return Action.LOW_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                if randNum <= 95:
                    if Action.MIN_BET in validActions:
                        return Action.MIN_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                if randNum > 95:
                    if Action.CALL in validActions:
                        return Action.CALL
                    elif Action.CHECK in validActions:
                        return Action.CHECK
                    else:
                        return Action.ALL_IN
                    
            elif policyRank == 3:
                # Strong hand
                # 0% all in, 5% high bet, 15% mid bet, 25% low bet, 40% min bet, 15% call/check, 0% fold
                randNum = randrange(1,100)
                if randNum <= 5:
                    if Action.HIGH_BET in validActions:
                        return Action.HIGH_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                elif randNum <= 20:
                    if Action.MID_BET in validActions:
                        return Action.MID_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                elif randNum <= 45:
                    if Action.LOW_BET in validActions:
                        return Action.LOW_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                elif randNum <= 85:
                    if Action.MIN_BET in validActions:
                        return Action.MIN_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                if randNum > 85:
                    if Action.CALL in validActions:
                        return Action.CALL
                    elif Action.CHECK in validActions:
                        return Action.CHECK
                    else:
                        return Action.ALL_IN
                    
            elif policyRank == 4:
                # Decent hand
                # 0% all in, 0% high bet, 5% mid bet, 15% low bet, 40% min bet, 30% call/check, 0% fold
                randNum = randrange(1,100)
                if randNum <= 5:
                    if Action.MID_BET in validActions:
                        return Action.MID_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                elif randNum <= 20:
                    if Action.LOW_BET in validActions:
                        return Action.LOW_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                elif randNum <= 60:
                    if Action.MIN_BET in validActions:
                        return Action.MIN_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                if randNum > 60:
                    if Action.CALL in validActions:
                        return Action.CALL
                    elif Action.CHECK in validActions:
                        return Action.CHECK
                    else:
                        return Action.ALL_IN
                    
            elif policyRank == 5:
                # Weak hand
                # 0% all in, 0% high bet, 0% mid bet, 5% low bet, 30% min bet, 65% call/check, 0% fold
                randNum = randrange(1,100)
                if randNum <= 5:
                    if Action.LOW_BET in validActions:
                        return Action.LOW_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                if randNum <= 35:
                    if Action.MIN_BET in validActions:
                        return Action.MIN_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                if randNum > 35:
                    if Action.CALL in validActions:
                        return Action.CALL
                    elif Action.CHECK in validActions:
                        return Action.CHECK
                    else:
                        return Action.FOLD
                    
            elif policyRank == 6:
                # Very weak hand
                # 0% all in, 0% high bet, 0% mid bet, 0% low bet, 20% min bet, 80% call/check, 0% fold
                randNum = randrange(1,100)
                if randNum <= 20:
                    if Action.MIN_BET in validActions:
                        return Action.MIN_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                if randNum > 20:
                    if Action.CALL in validActions:
                        return Action.CALL
                    elif Action.CHECK in validActions:
                        return Action.CHECK
                    else:
                        return Action.FOLD
                    
            elif policyRank == 7:
                # One of the worst hands
                # 0% all in, 0% high bet, 0% mid bet, 0% low bet, 5% min bet, 95% call/check, 0% fold
                randNum = randrange(1,100)
                if randNum <= 5:
                    if Action.MIN_BET in validActions:
                        return Action.MIN_BET
                    elif Action.OP_MAX in validActions:
                        return Action.OP_MAX
                    else:
                        randNum = 100
                if randNum > 5:
                    if Action.CALL in validActions:
                        return Action.CALL
                    elif Action.CHECK in validActions:
                        return Action.CHECK
                    else:
                        return Action.FOLD
                    
            elif policyRank == 8:
                # 0% all in, 0% high bet, 0% mid bet, 0% low bet, 0% min bet, 90% call/check, 10% fold
                randNum = randrange(1,100)
                if randNum <= 10:
                    return Action.FOLD
                else:
                    if Action.CALL in validActions:
                        return Action.CALL
                    elif Action.CHECK in validActions:
                        return Action.CHECK
                    else:
                        return Action.FOLD
                
            elif policyRank == 9:
                # 0% all in, 0% high bet, 0% mid bet, 0% low bet, 0% min bet, 60% call/check, 40% fold
                randNum = randrange(1,100)
                if randNum <= 40:
                    return Action.FOLD
                else:
                    if Action.CALL in validActions:
                        return Action.CALL
                    elif Action.CHECK in validActions:
                        return Action.CHECK
                    else:
                        return Action.FOLD
                    
            elif policyRank == 10:
                # 0% all in, 0% high bet, 0% mid bet, 0% low bet, 0% min bet, 40% call/check, 60% fold
                randNum = randrange(1,100)
                if randNum <= 60:
                    return Action.FOLD
                else:
                    if Action.CALL in validActions:
                        return Action.CALL
                    elif Action.CHECK in validActions:
                        return Action.CHECK
                    else:
                        return Action.FOLD
                    
            else:
                # 0% all in, 0% high bet, 0% mid bet, 0% low bet, 0% min bet, 20% call/check, 80% fold
                randNum = randrange(1,100)
                if randNum <= 80:
                    return Action.FOLD
                else:
                    if Action.CALL in validActions:
                        return Action.CALL
                    elif Action.CHECK in validActions:
                        return Action.CHECK
                    else:
                        return Action.FOLD


                

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

            self.chipsWon = 0
            self.chipsWonSqrt = 0

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
            
            self.availableActions = MonteCarloAgent.MCTree.getValidPlayerActions(self, self.board)
            # # Remove FOLD option, it should not occur in tree????
            # self.availableActions.remove(Action.FOLD)

        
    
    
    def MONTE_CARLO_TREE_SEARCH(self, board, numSim):
        # TODO: follow pseudocode
        tree = MonteCarloAgent.MCTree(board)
        for i in range(numSim):
            leaf = tree.SELECT()
            child = tree.EXPAND(leaf)
            # NOTE: SIMULATE has not been implemented
            # print("simulation", i)
            result = tree.SIMULATE(child)
            tree.BACK_PROPAGATE(result, child)

        maxNumPlayouts = None
        chosenNode = None
        for i in range(tree.root.children.__len__()):
            node = tree.root.children[i]
            numPlayouts = MonteCarloAgent.MCTree.N(node)
            # numPlayouts = MonteCarloAgent.MCTree.U(node) / MonteCarloAgent.MCTree.N(node)
            # numPlayouts = MonteCarloAgent.MCTree.U(node)
            # print("Node: " + str(node.playerAction) + " Playouts: " + str(MonteCarloAgent.MCTree.N(node)) + " U: " + str(MonteCarloAgent.MCTree.U(node)))
            if maxNumPlayouts is None or numPlayouts > maxNumPlayouts or (numPlayouts == maxNumPlayouts and MonteCarloAgent.MCTree.U(node) > MonteCarloAgent.MCTree.U(chosenNode)):
                maxNumPlayouts = numPlayouts
                chosenNode = node
        chosenAction = chosenNode.playerAction
        # print("Chosen Action: " + str(chosenAction))
        return chosenAction






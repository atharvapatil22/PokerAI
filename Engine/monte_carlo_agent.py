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
        action = self.MONTE_CARLO_TREE_SEARCH(board, 1000)
        print(f"Monte Carlo Agent chose: {action}")
        return action
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
            self.agentIndex = copy.deepcopy(boardState.activePlayerIndex)
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

            # Disable checking if enabled
            if board.checkFlag:
                board.checkFlag = False
                # Not needed after the Phase Change Logic Fix
                # for i in range(self.board.playersPassing.__len__()):
                #     self.board.playersPassing[i] = False

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

        def SIMULATENEW(self, node):
            simulatedBoard = copy.deepcopy(node.board)

            opponentIdx = (self.agentIndex + 1) % simulatedBoard.players.__len__()
            # The index of the player who made the choice can be derived from the isAgent field
            #   The index of the player who made the choice, is the player BEFORE the active player
            simulatedIndex = self.agentIndex if node.isAgent else opponentIdx

            copy.deepcopy((simulatedBoard.activePlayerIndex + 1) % simulatedBoard.players.__len__())

            #create newly randomized deck
            randDeck = Deck(True, None)
            #remove cards that are in the agent's hand and community
            removeCards = simulatedBoard.players[self.agentIndex].cardsInHand + self.root.board.community
            #remove cards that are in the agent's hand and community
            for cardToRemove in removeCards:
                for card in randDeck.cards:
                    if str(card) == str(cardToRemove):
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
                availableSimActions = MonteCarloAgent.MCTree.getValidPlayerActions(simulatedBoard)
                randomActionIdx = randrange(availableSimActions)
                randomAction = availableSimActions[randomActionIdx]
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
                        for i in range(self.players.__len__()):
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
                return (simulatedBoard.pot / 2)
            else:
                # Player who made choice resulting in node, lost
                return -(simulatedBoard.pot / 2)

            

            
        # Run a simulation on the given node
        #   This is where a deck sequence is generated based off of what we know (board variable of node)
        #   Return [amount], where amount is the amount won in the round. (positive is win) (0 is tie (two player game)) (negative is loss)
        def SIMULATE(self, node):
            simulatedNode = copy.deepcopy(node)
            
            # # reset board
            # for i in range(simulatedNode.board.players.__len__()):
            #     print(simulatedNode.board.playersPassing[i])
            #     print(simulatedNode.board.playersFolding[i])
            #     print(simulatedNode.board.playersAllIn[i])
            #     simulatedNode.board.playersPassing[i] = False
            #     simulatedNode.board.playersFolding[i] = False
            #     simulatedNode.board.playersAllIn[i] = False
            print("Simulate phase: " + str(simulatedNode.board.phase))
            community = copy.deepcopy(simulatedNode.board.community) #copy current community, should be the real-time community card
            #create newly randomized deck
            randDeck = Deck(True, None)
            #remove cards that are in the agent's hand and community
            removeCards = simulatedNode.board.players[self.root.board.activePlayerIndex].cardsInHand + self.root.board.community
            #remove cards that are in the agent's hand
            for card_in_hand in removeCards:
                    for card in randDeck.cards:
                        if str(card) == str(card_in_hand):
                            randDeck.cards.remove(card)
                            break
            #provide randomized hand to the non-agent opponent
            opponentIdx = (self.root.board.activePlayerIndex + 1) % simulatedNode.board.players.__len__()
            simulatedNode.board.players[opponentIdx].cardsInHand = [randDeck.top(), randDeck.top()]

            simPhaseDiff = simulatedNode.board.phase - self.root.board.phase #see if board is not in same phase as real game
            if simPhaseDiff > 0: #if simulation is not synced, fill in community cards
                # print("Simulating phase difference")    
                if community.__len__() == 0 and simulatedNode.board.phase >= 2: #if past phase 1 and no community cards, add them
                    for _ in range(3):
                        # print("Added 3 community card")
                        community.append(randDeck.top())
                if community.__len__() == 3 and simulatedNode.board.phase >= 3: #if past phase 2 and only 3 community cards, add them
                    community.append(randDeck.top())
                if simulatedNode.board.phase >= 4: # if phase 4 or 5, add last community card
                    # print("Added community card")
                    community.append(randDeck.top())
                    # print("Community length: " + str(len(community)))

            if simulatedNode.board.phase == 5: #if board is in scoring phase, evaluate
                scores = [None, None] 
                folded = False
                for i in range(node.board.players.__len__()):
                    if node.board.playersFolding[i]: #if player folded, set score to 0 and the other to 1
                        scores[i] = 0
                        scores[(i + 1) % 2] = 1
                        folded = True
                        break
                if(not folded): # if no players folded, calculate their score
                    for pl in node.board.players:
                        hand = pl.cardsInHand + community
                        scores[pl.id - 1] = MonteCarloAgent.handScore(hand) 
                        # I had to adjust this code because handScore expects a 7 card hand and that's not possible if a player folds because the game ends prematurely
                
                playerScore = scores[self.root.board.activePlayerIndex]
                maxScore = max(scores)

                if playerScore != maxScore:
                    return -1
                else:
                    for p in range(len(scores)):
                        if p != self.root.board.activePlayerIndex and scores[p] == maxScore:
                            return 0
                        else: 
                            return 1 
            else:
                end = False
                while(not end):
                    # Given board state, determine active player action
                    # Update board state with active player action
                    # Keep going until both players are passive
                    
                    randomActionIdx = randrange(simulatedNode.availableActions.__len__())
                    randomAction = simulatedNode.availableActions[randomActionIdx]
                    # TODO: Perform the action on newBoard!!!
                    # NOTE: This can likely be done by copying some methods from round, making them static, and then using them.
                    #       These new static methods should be made in such a way that they can be used in the simulations too!
                    # print("players passing: ",simulatedNode.board.playersPassing)
                    
                    # Handle player action
                    print("Random Action: " + str(randomAction) +" player index: "+str(simulatedNode.board.activePlayerIndex))
                    if randomAction in [Action.MIN_BET,Action.LOW_BET,Action.MID_BET,Action.HIGH_BET]:
                        self.handleBet(simulatedNode.board,randomAction)
                    elif randomAction == Action.ALL_IN:
                        self.handleAllIn(simulatedNode.board)
                    elif randomAction == Action.OP_MAX:
                        self.handleOpMax(simulatedNode.board)
                    elif randomAction == Action.CALL:
                        self.handleCall(simulatedNode.board)
                    elif randomAction == Action.CHECK:
                        # Passing
                        simulatedNode.board.playersPassing[simulatedNode.board.activePlayerIndex] = True
                    elif randomAction == Action.FOLD:
                        # Folded
                        print("Player " + str(simulatedNode.board.activePlayerIndex) + " folded")
                        simulatedNode.board.playersFolding[simulatedNode.board.activePlayerIndex] = True
                        # Passing
                        simulatedNode.board.playersPassing[simulatedNode.board.activePlayerIndex] = True
                        simulatedNode.board.phase = 5
                        return self.SIMULATE(simulatedNode) 

                    # After accounting for the applied action, it is now the next player's turn
                    simulatedNode.board.activePlayerIndex += 1
                    simulatedNode.board.activePlayerIndex = (simulatedNode.board.activePlayerIndex) % simulatedNode.board.players.__len__()
                    
                    
                    
                    # end = MonteCarloAgent.MCTree.endTurn(simulatedNode.board)

                    # # This method will return True if phase is changed, repeat until it returns false,
                    # # or if the phase is 5 (end state)
                    end = MonteCarloAgent.MCTree.phaseChangeCheck(simulatedNode.board)
                    # phaseChange = True
                    # while phaseChange:
                    #     phaseChange = MonteCarloAgent.MCTree.phaseChangeCheck(simulatedNode.board)
                    #     if simulatedNode.board.phase == 5:
                    #         phaseChange = False

                    # print("players all in",simulatedNode.board.playersAllIn)
                    # print("End phase?", end)
                    # simulatedNode.board.phase += 1 this is done in phaseChangeCheck
                # Call simulate again but with a new phase
                simulatedNode.board.community = community
                return self.SIMULATE(simulatedNode) 


            



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
            print("Result: " + str(result))
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
            print("simulation", i)
            result = tree.SIMULATE(child)
            tree.BACK_PROPAGATE(result, child)

        maxNumPlayouts = None
        chosenNode = None
        for i in range(tree.root.children.__len__()):
            node = tree.root.children[i]
            numPlayouts = MonteCarloAgent.MCTree.N(node)
            print("Node: " + str(node.playerAction) + " Playouts: " + str(numPlayouts) + " U: " + str(MonteCarloAgent.MCTree.U(node)))
            if maxNumPlayouts is None or numPlayouts > maxNumPlayouts or (numPlayouts == maxNumPlayouts and MonteCarloAgent.MCTree.U(node) > MonteCarloAgent.MCTree.U(chosenNode)):
                maxNumPlayouts = numPlayouts
                chosenNode = node
        chosenAction = chosenNode.playerAction
        return chosenAction






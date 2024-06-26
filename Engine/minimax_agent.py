import random
import copy
import itertools
import math
import collections
from agent import Agent
from player import Action,BetRatio
from CONSTANTS import Preflop_Handscores,CheckPairTypes

# This agent can only handle 2player poker. It will have to be modified for multiplayer games.
class MinimaxAgent(Agent):
    # ~~refactor : Similar function is required in round and maybe some other places. This should be refactored to be DRY
    # def: Function will return possible actions for a player at this game_state
    def possiblePlayerActions(self,game_state,p_index):
        playerData = game_state['players'][p_index]
        validActions = [Action.FOLD, Action.CALL, Action.CHECK, Action.ALL_IN, Action.LOW_BET, Action.MID_BET, Action.HIGH_BET]
        
        incomingBet = game_state['currentBet'] - playerData['bet']
        
        if incomingBet == 0:
            validActions.remove(Action.CALL) 
        if incomingBet > playerData['chipsRemaining']:
            if Action.CALL in validActions: validActions.remove(Action.CALL) 
            validActions.remove(Action.LOW_BET)
            validActions.remove(Action.MID_BET)
            validActions.remove(Action.HIGH_BET)
        if incomingBet != 0:
            validActions.remove(Action.CHECK)
        if incomingBet > (playerData['chipsRemaining'] * BetRatio.LOW_BET):
            if Action.LOW_BET in validActions: validActions.remove(Action.LOW_BET)
        if incomingBet > (playerData['chipsRemaining'] * BetRatio.MID_BET):
            if Action.MID_BET in validActions: validActions.remove(Action.MID_BET)
        if incomingBet > (playerData['chipsRemaining'] * BetRatio.HIGH_BET):
            if Action.HIGH_BET in validActions: validActions.remove(Action.HIGH_BET)
        return validActions

    # ~~refactor : Similar logic is used in round Class. This should be refactored to be DRY
    # def: Takes in game_state and player action, and returns updated game state (without modifying the current gs)
    def getUpdatedGameState(self,game_state,action,p_index):
        new_game_state = copy.deepcopy(game_state)
        playerData = new_game_state['players'][p_index]
        incomingBet = new_game_state['currentBet'] - playerData['bet']
        
        playerData['acted'] = True
        if action == Action.FOLD:
            new_game_state['players'].pop(p_index)
        elif action == Action.CALL:
            playerData['bet'] += incomingBet
            playerData['chipsRemaining'] -= incomingBet
            new_game_state['pot'] += incomingBet
        elif action == Action.ALL_IN:
            playerData['bet'] += playerData['chipsRemaining']
            new_game_state['pot'] += playerData['chipsRemaining']
            if playerData['chipsRemaining'] > incomingBet:
                new_game_state['currentBet'] = playerData['bet']
            playerData['chipsRemaining'] = 0 
        elif action == Action.LOW_BET:
            playerData['bet'] += (playerData['chipsRemaining'] * BetRatio.LOW_BET)
            new_game_state['pot'] += (playerData['chipsRemaining'] * BetRatio.LOW_BET)
            if (playerData['chipsRemaining'] * BetRatio.LOW_BET) > incomingBet:
                new_game_state['currentBet'] = playerData['bet']
            playerData['chipsRemaining'] -= (playerData['chipsRemaining'] * BetRatio.LOW_BET)
        elif action == Action.MID_BET:
            playerData['bet'] += (playerData['chipsRemaining'] * BetRatio.MID_BET)
            new_game_state['pot'] += (playerData['chipsRemaining'] * BetRatio.MID_BET)
            if (playerData['chipsRemaining'] * BetRatio.MID_BET) > incomingBet:
                new_game_state['currentBet'] = playerData['bet']
            playerData['chipsRemaining'] -= (playerData['chipsRemaining'] * BetRatio.MID_BET)
        elif action == Action.HIGH_BET:
            playerData['bet'] += (playerData['chipsRemaining'] * BetRatio.HIGH_BET)
            new_game_state['pot'] += (playerData['chipsRemaining'] * BetRatio.HIGH_BET)
            if (playerData['chipsRemaining'] * BetRatio.HIGH_BET) > incomingBet:
                new_game_state['currentBet'] = playerData['bet']
            playerData['chipsRemaining'] -= (playerData['chipsRemaining'] * BetRatio.HIGH_BET)
                
        return new_game_state
  
    # Checks if a betting-round/phase is over based on game_state
    def isPhaseOver(self,game_state):
        if len(game_state['players']) == 1: return True
        for player in game_state['players']:
            if player['acted']==False or (player['bet'] != game_state['currentBet'] and player['chipsRemaining']>0):
                return False
        return True
    
    # Function will take a value in range and normalize it to a corresponding value in new range
    def transformRange(self,old_value,old_range,new_range):
        
        # Extract values
        old_min = old_range[0]
        old_max = old_range[1]
        new_min = new_range[0]
        new_max = new_range[1]
        
        old_diff = (old_max - old_min)  
        new_diff = (new_max - new_min)  

        new_value = (((old_value - old_min) * new_diff) / old_diff) + new_min
        
        # Handle edge cases
        if new_value<new_min:
            new_value=new_min
        elif new_value>new_max:
            new_value=new_max
        
        return round(new_value,2)

    # Returns utility value for a leaf node:
    def getUtility(self,game_state):
        # pot_score is a rating (0.1-100) which determines how high or low is the ammount in pot
        # _refactor: Remove hardcoding => (pot/(num_players * starting_chips)) * 100
        pot_score = (game_state['pot']/(2 * 100)) * 100
        if pot_score > 100: pot_score = 100
        elif pot_score < 0.1: pot_score = 0.1

        # hand_score determines the score of the current hand. This is a range (0.1-100)
        hand_score = self.hand_strength(game_state['community'],self.cardsInHand)
        if hand_score == None or hand_score < 0.1: hand_score = 0.1  
        elif hand_score > 100: hand_score = 100

        product = hand_score * pot_score

        # These ranges are hard-coded for desired agent behaviour
        if hand_score > 66.0:
            # HIGH hand | HIGH pot
            if pot_score > 66.0:
                product_range = [4356,10000]
                utility_range = [60,100]
            # HIGH hand | MED pot
            elif pot_score > 33.0:
                product_range = [2178,6600]
                utility_range = [40,60]
            # HIGH hand | LOW pot
            else:
                product_range = [6.6,3300]
                utility_range = [0,40]
        elif hand_score > 33.0:
            # MED hand | HIGH pot
            if pot_score > 66.0:
                product_range = [2178,6600]
                utility_range = [0,30]
            # MED hand | MED pot
            elif pot_score > 33.0:
                product_range = [1089,4356]
                utility_range = [60,100]
            # MED hand | LOW pot
            else:
                product_range = [3.3,2178]
                utility_range = [30,60]
        else: 
            # LOW hand | HIGH pot
            if pot_score > 66.0:
                product_range = [6.6,3300]
                utility_range = [0,50]
            # LOW hand | MED pot
            elif pot_score > 33.0:
                product_range = [3.3,2178]
                utility_range = [50,80]
            # LOW hand | LOW pot
            else:
                product_range = [0.01,1089]
                utility_range = [80,100]
        return self.transformRange(product,product_range,utility_range)

    def minimax_search(self,game_state):
        v,action = self.max_value(game_state,0,[float('-inf'),float('inf')])
        return action
  
    def max_value(self,game_state,level,alpha_beta):
        # If game-state marks the end of phase, return utility value
        if self.isPhaseOver(game_state) or level > 10:
            util = self.getUtility(game_state)
            return util, None
        
        v = float('-inf')
        action = None
        
        # possible actions for maximizing player 
        possibleActions = self.possiblePlayerActions(game_state,0)

        for ac in possibleActions:
            new_gs = self.getUpdatedGameState(game_state,ac,0)
            v2,a2 = self.min_value(new_gs,level+1,alpha_beta)
            
            if v2 > v:
                v = v2
                action = ac

            # prune if v >= Beta
            if v>=alpha_beta[1]:
                return v,action
            # update Alpha
            if v > alpha_beta[0]:
                alpha_beta[0] = v

        return v,action
  
    def min_value(self,game_state,level,alpha_beta):
        # If game-state marks the end of phase, return utility value
        if self.isPhaseOver(game_state) or level > 10:
            util = self.getUtility(game_state)
            return util, None
        
        v = float('inf')
        action = None

        # possible actions for minimizing player
        possibleActions = self.possiblePlayerActions(game_state,1)

        for ac in possibleActions:
            new_gs = self.getUpdatedGameState(game_state,ac,1)
            v2,a2 = self.max_value(new_gs,level+1,alpha_beta)
            if v2 < v:
                v = v2
                action = ac

            # prune if v < Alpha
            if v <= alpha_beta[0]:
                return v,action
            # update Beta
            if v < alpha_beta[1]:
                alpha_beta[1] = v
        return v,action
  
    # In the current implementation, Minimax search is using a different representation of the board called game state. 
    # This function should be removed later and code should be refactored to have same representation between engine and agents
    def make_game_state_from_board(self,board):
        game_state ={}
        game_state['pot'] = board.pot
        game_state['currentBet'] = board.currentBet
        game_state['community'] = board.community
        game_state['players'] = []
        game_state['minBet'] = board.minBet
        for i in range(board.players.__len__()):
            game_state['players'].append({'bet':board.playerBets[i],'chipsRemaining':board.players[i].chips,'acted':board.playersPassing[i]})

        # game_state ={}
        # game_state['pot'] = board['pot']
        # game_state['currentBet'] = board['currentBet']
        # game_state['community'] = board['community']
        # game_state['players'] = []
        # game_state['minBet'] = board['minBet']
        # for i in range(board['players'].__len__()):
        #     game_state['players'].append({'bet':board['playerBets'][i],'chipsRemaining':board['players'][i]['chips'],'acted':board['playersPassing'][i]})

        return game_state
  
    def get_action(self, board, validActions):
        # game_state = {
        # 'players': [{'bet':25,'chipsRemaining':30,'acted':False},{'bet':50,'chipsRemaining':40,'acted':False}],
        # 'pot': 75,
        # 'currentBet':50,
        # }
        game_state = self.make_game_state_from_board(board)

        # NOTE: Current implementation of search will only search till the end of current phase.
        res = self.minimax_search(game_state)
        return res
    
    def hand_strength(self, community, cardsInHand):

        # For pre-flop phase
        if len(community) == 0:
            handCard1 = cardsInHand[0].value
            handCard2 = cardsInHand[1].value
            for key,val in Preflop_Handscores.items():
                c1,c2 = key
                if( (c1==handCard1 and c2==handCard2) or (c1==handCard2 and c2==handCard1)):
                    return val
            return 0.1
        
        # For Flop,Turn,River phases
        else:
            totalCards = community + cardsInHand
            combinations = list(itertools.combinations(totalCards, 5))

            hand_score = 0.1

            for comb in combinations:
                sorted_hand = sorted(comb, key=lambda card: card.value)

                # The probabilities of the first 6 ranks is less than 1%, so directly return if these are encountered
                if self.is_royal_flush(sorted_hand):
                    return 100
                elif self.is_straight_flush(sorted_hand):
                    return 98
                elif self.is_four_of_a_kind(sorted_hand):
                    return 96
                elif self.is_full_house(sorted_hand):
                    return 94
                elif self.is_flush(sorted_hand):
                    return 92
                elif self.is_straight(sorted_hand):
                    return 90
                
                # For the following ranks, dont return directly
                pairs_response = self.check_pairs(sorted_hand)

                if pairs_response['type'] == CheckPairTypes.THREE_KIND:
                    temp_score = 80
                    hand_score = max(hand_score,temp_score)
                elif pairs_response['type'] == CheckPairTypes.TWO_PAIR:
                    pair_value = pairs_response['pairedCards'][0] + pairs_response['pairedCards'][1]
                    temp_score = self.transformRange(pair_value,[0,24],[60,80])
                    hand_score = max(hand_score,temp_score)
                elif pairs_response['type'] == CheckPairTypes.ONE_PAIR:
                    temp_score = self.transformRange(pairs_response['pairedCards'][0],[0,12],[30,60])
                    hand_score = max(hand_score,temp_score)
                # case for high card
                elif pairs_response['type'] == None:
                    temp_score = self.transformRange(pairs_response['highestCard'],[0,12],[0,30])
                    hand_score = max(hand_score,temp_score)
                
            return hand_score
        
            # --------- ⬇ OLD HAND SCORE LOGIC ⬇ ---------
            # for comb in combinations:
            #     sorted_hand = sorted(comb, key=lambda card: card.value)
            #     if self.is_straight_flush(sorted_hand):
            #         handscore = 100
            #         for i in range(14, 0, -1):
            #             if i == comb[4].value and i == 14:
            #                 return handscore
            #             elif i == comb[4].value: 
            #                 return handscore - (13/14)
            #     elif self.is_four_of_a_kind(sorted_hand)[0]:
            #         handscore = 87
            #         for i in range(14, 0, -1):
            #             if i == self.is_four_of_a_kind(sorted_hand)[1] and i == 14:
            #                 return handscore
            #             elif i == self.is_four_of_a_kind(sorted_hand)[1]: 
            #                 return handscore - (13/14)
            #     elif self.is_full_house(sorted_hand)[0]:
            #         handscore = 74
            #         for i in range(14, 0, -1):
            #             if i == self.is_full_house(sorted_hand)[1] and i == 14:
            #                 return handscore
            #             elif i == self.is_full_house(sorted_hand)[1]: 
            #                 return handscore - (13/14)
            #     elif self.is_flush(sorted_hand):
            #         handscore = 61
            #         for i in range(14, 0, -1):
            #             if i == comb[4].value and i == 14:
            #                 return handscore
            #             elif i == comb[4].value: 
            #                 return handscore - (13/14)
            #     elif self.is_straight(sorted_hand):
            #         handscore = 48
            #         for i in range(14, 0, -1):
            #             if i == comb[4].value and i == 14:
            #                 return handscore
            #             elif i == comb[4].value: 
            #                 return handscore - (13/14)
            #     elif self.is_three_of_a_kind(sorted_hand)[0]:
            #         handscore = 35
            #         for i in range(14, 0, -1):
            #             if i == self.is_three_of_a_kind(sorted_hand)[1] and i == 14:
            #                 return handscore
            #             elif i == self.is_three_of_a_kind(sorted_hand)[1]: 
            #                 return handscore - (13/14)
            #     elif self.is_two_pair(sorted_hand):
            #         handscore = 22
            #         for i in range(14, 0, -1):
            #             if i == comb[3].value and i == 14:
            #                 return handscore
            #             elif i == comb[3].value: 
            #                 return handscore - (13/14)
            #     elif self.is_one_pair(sorted_hand):
            #         # handscore = 9
            #         # for i in range(14, 0, -1):
            #         #     if i == self.is_one_pair(sorted_hand)[1] and i == 14:
            #         #         return handscore
            #         #     elif i == self.is_one_pair(sorted_hand)[1]: 
            #         #         return handscore - (9/14)
            #         handscore = 7
            #         highest_card = float('-inf')
            #         for card in sorted_hand:
            #             if card.value > highest_card:
            #                 highest_card = card.value
            #         return handscore + ((highest_card/14)*4)
            #     else:
            #         return 0
            # --------- ⬆ OLD HAND SCORE LOGIC ⬆ --------- 
    
    def is_royal_flush(self,hand):
        if all(card.value > 9 for card in hand) and self.is_flush(hand) and self.is_straight(hand):
            return True
        else: return False

    def is_straight_flush(self,hand):
        suits_set = set(card.suit for card in hand)
        if len(suits_set) == 1:
            for i in range(1, len(hand)):
                if hand[i].value != hand[i-1].value + 1:
                    return False
            return True
        return False
    def is_four_of_a_kind(self,hand):
        # Check for Four of a Kind logic
        rank_counts = [0] * 13
        for card in hand:
            rank_counts[card.value-2] += 1
        for index,count in enumerate(rank_counts):
            if count == 4:
                return True, index 
        return False, -1

    def is_full_house(self,hand):
        # Check for Full House logic
        rank_counts = [0] * 13
        for card in hand:
            rank_counts[card.value-2] += 1
        for idx, count in enumerate(rank_counts):
            if count == 3:
                for count in rank_counts:
                    if count == 2:
                        return True, idx
        return False, -1

    def is_flush(self,hand):
        # Check for Flush logic
        suits_set = set(card.suit for card in hand)
        return len(suits_set) == 1

    def is_straight(self,hand):
        # Check for Straight logic
        for i in range(1, len(hand)):
            if hand[i].value != hand[i-1].value + 1:
                return False
        return True

    # Function will check if a hand has THREE_KIND or TWO_PAIR or ONE_PAIR and return the paired cards, if no pairs are found it will return the highest card
    # returns: {'type': THREE_KIND/TWO_PAIR/ONE_PAIR/None ,'pairedCards': list,'highestCard':value}
    def check_pairs(self,hand):
        
        # Encode cards into a rank counts list like this:
        # Card Vals ->   #2 3 4 5 6 7 8 9 10 J Q K A
        # rank_counts -> [0,0,0,1,0,0,1,0,2, 0,1,0,0]
        rank_counts = [0] * 13
        for card in hand:
            rank_counts[card.value-2] += 1

        response = {'type':None ,'pairedCards':[],'highestCard':None}
        pair_found = False 
        
        for index,count in enumerate(rank_counts):
            # if three of a kind is found return immediately
            if count == 3:
                response['type'] = CheckPairTypes.THREE_KIND
                response['pairedCards'].append(index)
                return response
            # if two of a kind is found, check for more pairs
            elif count == 2:
                if not pair_found:
                    pair_found = True
                    response['type'] = CheckPairTypes.ONE_PAIR
                    response['pairedCards'].append(index)
                else:
                    response['type'] = CheckPairTypes.TWO_PAIR
                    response['pairedCards'].append(index)
                    return response
            # keep updating the highest card. This will be returned if no pairs are found
            elif count == 1 and not pair_found:
                response['highestCard'] = index 
        
        return response  


    # --------- ⬇ OLD HAND SCORE LOGIC ⬇ ---------
    # def is_three_of_a_kind(self,hand):
    #     # Check for Three of a Kind logic
    #     rank_counts = [0] * 13
    #     for card in hand:
    #         rank_counts[card.value-2] += 1
    #     for index,count in enumerate(rank_counts):
    #         if count == 3:
    #             return True, index 
    #     return False, -1

    # def is_two_pair(self,hand):
    #     # Check for Two Pair logic
    #     rank_counts = collections.Counter(card.value for card in hand)
    #     num_pairs = 0
    #     for count in rank_counts.items():
    #         if count == 2:
    #             num_pairs += 1
    #     return num_pairs == 2

    # def is_one_pair(self,hand):
    #     # Check for One Pair logic
    #     rank_counts = [0] * 13
        
    #     for card in hand:
    #         rank_counts[card.value-2] += 1
    #     for index,count in enumerate(rank_counts):
    #         if count == 2:
    #             return True, index 
    #     return False, -1
    # --------- ⬆ OLD HAND SCORE LOGIC ⬆ ---------          
            




from player import Player
from player import Action
from agent import Agent
from deck import Deck

class SimulationAgent(Agent):

    def get_action(self, board, validActions):
        cards_in_hand = self.cardsInHand # Player current cards
        community_cards = board.community # Current community cards
        cards_to_remove = cards_in_hand + community_cards # Cards we don't want in the deck so we don't get them twice
        your_wins = 0
        opponent_wins = 0
        ties = 0
        simulations = 10
        for _ in range(simulations):
            deck = Deck(True, None)
            for card_to_remove in cards_to_remove: # Remove cards we don't want to get twice from the deck
                for card in deck.cards:
                    if card.id == card_to_remove.id:
                        deck.cards.remove(card)
                        break
            # print(len(deck.cards))
            opponent_hand = [deck.top(), deck.top()] + community_cards # Opponent hand
            hand = cards_in_hand + community_cards # Your hand
            randomized_community_cards = []
            for _ in range(5-len(community_cards)): # Simulate the rest of the community cards
                randomized_community_cards.append(deck.top())
            opponent_hand += randomized_community_cards
            hand += randomized_community_cards
            hand_score = SimulationAgent.handScore(hand) # Score your simulated hand
            opponent_score = SimulationAgent.handScore(opponent_hand) # Score opoonents simulated hand
            if hand_score > opponent_score: # Determine winner
                your_wins +=1
            elif hand_score == opponent_score:
                ties +=1
            else:
                opponent_wins +=1
        your_win_percentage = (your_wins+0.5*ties)/(simulations)
        import random as rnd
        random_number = rnd.random() # Leaving this in here but the randomness made it WAY worse (75% vs 40% win rate)
        # print(your_win_percentage)
        # print(random_number)
        if(your_win_percentage > 0.6): # If you have a very good hand, be very aggressive
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
        if(your_win_percentage > 0.5): # If a fairly good hand, be slightly aggressive
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
        elif(your_win_percentage > 0.4): # If an okay hand, be passive
            if(random_number < 0.3): # some randomness, 30% chance of being aggressive with a mid hand
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
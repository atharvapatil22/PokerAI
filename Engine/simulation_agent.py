from player import Player
from player import Action
from agent import Agent
from deck import Deck

class SimulationAgent(Agent):

    def get_action(self, board, validActions):
        cards_in_hand = self.cardsInHand
        community_cards = board.community
        your_wins = 0
        opponent_wins = 0
        ties = 0
        simulations = 10
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
            hand_score = SimulationAgent.handScore(hand)
            opponent_score = SimulationAgent.handScore(opponent_hand)
            if hand_score > opponent_score:
                your_wins +=1
            elif hand_score == opponent_score:
                ties +=1
            else:
                opponent_wins +=1
        your_win_percentage = (your_wins+0.5*ties)/(simulations)
        import random as rnd
        random_number = rnd.random() # Leaving this in here but the randomness made it WAY worse (75% vs 40% win rate)
        if(your_win_percentage > 0.6):
            if(random_number < 0.3): # some randomness, 30% chance of being passive with a good hand
                if(Action.CHECK in validActions):
                    return Action.CHECK
                return Action.CALL
            if(Action.MID_BET in validActions):
                return Action.MID_BET
            elif(Action.HIGH_BET in validActions):
                return Action.HIGH_BET
            else:
                return Action.ALL_IN
        elif(your_win_percentage > 0.4):
            if(random_number < 0.3): # some randomness, 30% chance of being aggressive with a mid hand
                if(Action.MID_BET in validActions):
                    return Action.MID_BET
                elif(Action.HIGH_BET in validActions):
                    return Action.HIGH_BET
                else:
                    return Action.ALL_IN
            if(Action.CHECK in validActions):
                return Action.CHECK
            return Action.CALL
        else:
            return Action.FOLD
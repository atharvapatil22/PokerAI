from player import Player
from player import Action
from agent import Agent
from deck import Deck

class MonteCarloAgent(Agent):

    def get_action(self, board, validActions):
        cards_in_hand = self.cardsInHand
        community_cards = board.community
        your_wins = 0
        opponent_wins = 0
        for _ in range(500):
            deck = Deck(True, None)
            for card in deck.cards:
                for card_in_hand in cards_in_hand:
                    if str(card) == str(card_in_hand):
                        deck.cards.remove(card)
            opponent_hand = [deck.top(), deck.top()]
            hand = cards_in_hand + community_cards
            opponent_hand = opponent_hand + community_cards
            randomized_community_cards = []
            for _ in range(7-len(hand)):
                randomized_community_cards.append(deck.top())
            opponent_hand += randomized_community_cards
            hand += randomized_community_cards
            hand_score = MonteCarloAgent.handScore(hand)
            opponent_score = MonteCarloAgent.handScore(opponent_hand)
            if hand_score > opponent_score:
                your_wins +=1
            else:
                opponent_wins +=1
        print(f"Your win percentage:", your_wins/500)
        return Action.CALL
    
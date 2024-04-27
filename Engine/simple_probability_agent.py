from player import Player
from player import Action, BetRatio
from agent import Agent
from random import randrange
from math import ceil

class SimpleProbabilityAgent(Agent):

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
        
    def get_action(self, board, validActions):
        cards_in_hand = board.players[board.activePlayerIndex].cardsInHand
        community_cards = board.community
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
            handScore = SimpleProbabilityAgent.handScore(cards_in_hand + community_cards)
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
                if Action.ALL_IN in validActions:
                    return Action.ALL_IN
            if randNum <= 25:
                if Action.HIGH_BET in validActions:
                    return Action.HIGH_BET
                randNum += 20
            if randNum <= 55:
                if Action.MID_BET in validActions:
                    return Action.MID_BET
                randNum += 30
            if randNum <= 95:
                if Action.LOW_BET in validActions:
                    return Action.LOW_BET
                randNum += 40
            if randNum <= 100:
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
                if Action.ALL_IN in validActions:
                    return Action.ALL_IN
            if randNum <= 10:
                if Action.HIGH_BET in validActions:
                    return Action.HIGH_BET
                randNum += 5
            if randNum <= 40:
                if Action.MID_BET in validActions:
                    return Action.MID_BET
                randNum += 30
            if randNum <= 80:
                if Action.LOW_BET in validActions:
                    return Action.LOW_BET
                randNum += 40
            if randNum <= 95:
                if Action.MIN_BET in validActions:
                    return Action.MIN_BET
                randNum += 15
            if randNum <= 100:
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
                randNum += 5
            if randNum <= 20:
                if Action.MID_BET in validActions:
                    return Action.MID_BET
                randNum += 15
            if randNum <= 40:
                if Action.LOW_BET in validActions:
                    return Action.LOW_BET
                randNum += 25
            if randNum <= 80:
                if Action.MIN_BET in validActions:
                    return Action.MIN_BET
                randNum += 40
            if randNum <= 95:
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
                randNum += 5
            if randNum <= 20:
                if Action.LOW_BET in validActions:
                    return Action.LOW_BET
                randNum += 15
            if randNum <= 60:
                if Action.MIN_BET in validActions:
                    return Action.MIN_BET
                randNum += 40
            if randNum <= 100:
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
                randNum += 5
            if randNum <= 35:
                if Action.MIN_BET in validActions:
                    return Action.MIN_BET
                randNum += 30
            if randNum <= 100:
                if Action.CALL in validActions:
                    return Action.CALL
                elif Action.CHECK in validActions:
                    return Action.CHECK
                else:
                    return Action.FOLD
                
        elif policyRank == 6:
            # Very weak hand
            # 0% all in, 0% high bet, 0% mid bet, 0% low bet, 20% min bet, 75% call/check, 0% fold
            randNum = randrange(1,100)
            if randNum <= 20:
                if Action.MIN_BET in validActions:
                    return Action.MIN_BET
                randNum += 20
            if randNum <= 100:
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
                randNum += 5
            if randNum <= 100:
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
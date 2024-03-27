from pokerPlayer import PokerPlayer
from deck import Deck

# general idea, poker will have rounds that take players array as parameters and return players array 
# play will continue until self.players array has size 1
# Within the rounds (might make a class for that), the rules of poker will be interpreted (might make a rules class???)
# So the button shenanigains (autobets) & turn order will be controlled from there. On each player's turn they can do the
# standard poker actions. Once everyone is neutral, the next community cards "stage" will begin, and the priority passing will continue.
# once everyone is done on the last stage, the score of hands will be calculated (using rules), and the player who wins will have the 
# pot added to their chips. Players with 0 remaining chips (or less chips than the minBet I guess?) will be removed from the players array
# and that array will be returned from the primary method of the Round

class Poker:

    def __init__(self, numPlayers, startChips, minBet) -> None:
        self.players = []
        for i in range(numPlayers):
            self.players.append(PokerPlayer(startChips, i+1))
        self.minBet = minBet
        self.buttonPlayerIndex = 0

    
    def runRound(self):
        # Define some variables
        deck = Deck()
        deck.shuffle()
        players = self.players
        playersPassing = []
        playersFolding = []
        for i in range(players.__len__()):
            playersFolding.append(False)
        activePlayerIndex = 0
        pot = 0
        community = []
        phase = 0


        # Small and Big blinds mandatory pay in
        if players.__len__() > 2:
            pot += players[(self.buttonPlayerIndex + 1) % players.__len__()].bet(self.minBet / 2)
            pot += players[(self.buttonPlayerIndex + 2) % players.__len__()].bet(self.minBet)
            activePlayerIndex = (self.buttonPlayerIndex + 3) % players.__len__()
        else:
            pot += players[(self.buttonPlayerIndex) % players.__len__()].bet(self.minBet / 2)
            pot += players[(self.buttonPlayerIndex + 1) % players.__len__()].bet(self.minBet)
            activePlayerIndex = (self.buttonPlayerIndex) % players.__len__()

        # Deal cards
        for i in range(players.__len__() * 2):
            players[(i+1+self.buttonPlayerIndex) % players.__len__()].dealt(deck.top())
        
        playerBets = []
        for i in range(players.__len__()):
            playersPassing.append(False)
            playerBets.append(0)

        # Initialize current bet
        currentBet = 0
        # Handle the blinds
        currentBet = self.minBet
        if players.__len__() > 2:
            playerBets[(self.buttonPlayerIndex + 1) % players.__len__()] = self.minBet / 2
            playerBets[(self.buttonPlayerIndex + 2) % players.__len__()] = self.minBet
        else: 
            playerBets[self.buttonPlayerIndex] = self.minBet / 2
            playerBets[(self.buttonPlayerIndex + 1) % players.__len__()] = self.minBet

        # Phases:
        # Phase 1: no community cards
        # Phase 2: 3 community cards
        # Phase 3: 4 community cards
        # Phase 4: 5 community cards
        
        # Start in phase 1
        phase = 1
        while phase < 5:
            for i in range(players.__len__()):
                if not playersFolding[i]:
                    playersPassing[i] = False
            # Handle the small blind going first in every phase after the first
            if not phase == 1:
                if players.__len__() > 2:
                    activePlayerIndex = self.buttonPlayerIndex + 1
                else:
                    activePlayerIndex = self.buttonPlayerIndex

            # Phases change once every player is folded or passing
            passing = False
            i = activePlayerIndex
            while (not passing):
                # Table turn cycle:
                print(f"i = {i}")
                # Set active player index
                activePlayerIndex = (i) % players.__len__()
                # Handle folded players
                if playersFolding[activePlayerIndex]:
                    print(f"Player {activePlayerIndex + 1} has folded.")
                    playersPassing[activePlayerIndex] = True
                    i += 1
                    continue
                # Print player interface
                print(f"Player {players[activePlayerIndex].id}, it is your turn.")
                communityString = "["
                for card in community:
                    communityString += f"{card}, "
                if community.__len__() > 0:
                    communityString = communityString[:-2] + "]"
                else:
                    communityString += "]"
                print(f"The community cards are: {communityString}.")
                print(f"Your hand is: {players[activePlayerIndex].hand()}.")
                print(f"You have {players[activePlayerIndex].chips} chips left.")
                print(f"You have bet {playerBets[activePlayerIndex]}.")
                print(f"The current bet is {currentBet}.")
                incomingBet = currentBet - playerBets[activePlayerIndex]
                print(f"The incoming bet is {incomingBet}.")
                # LOW_BET = 10%
                # MID_BET = 40%
                # HGH_BET = 70%
                # ALL_IN  = 100%
                # CALL = CHECK = Up to current bet
                # FOLD = drop out
                print(f'''
Your options are:
    MIN_BET ({incomingBet} + {self.minBet} = {incomingBet + self.minBet}) (raise)
    LOW_BET ({incomingBet} + {players[activePlayerIndex].chips * 0.1 if players[activePlayerIndex].chips * 0.1 > self.minBet else self.minBet} = {incomingBet + players[activePlayerIndex].chips * 0.1 if players[activePlayerIndex].chips * 0.1 > self.minBet else self.minBet}) (raise)
    MID_BET ({incomingBet} + {players[activePlayerIndex].chips * 0.4 if players[activePlayerIndex].chips * 0.4 > self.minBet else self.minBet} = {incomingBet + players[activePlayerIndex].chips * 0.4 if players[activePlayerIndex].chips * 0.1 > self.minBet else self.minBet}) (raise)
    HGH_BET ({incomingBet} + {players[activePlayerIndex].chips * 0.7 if players[activePlayerIndex].chips * 0.7 > self.minBet else self.minBet} = {incomingBet + players[activePlayerIndex].chips * 0.7 if players[activePlayerIndex].chips * 0.1 > self.minBet else self.minBet}) (raise)
    ALL_IN  ({players[activePlayerIndex].chips})
    CALL ({incomingBet})
    CHECK (only if incoming bet is 0)
    FOLD (drop out)
                    ''')
                # Request player action
                action = input("What will you do? (not case sensitive)\n")
                action = action.upper()
                # Handle player action
                if action == "MIN_BET":
                    # Calculate player bet
                    playerBet = incomingBet + self.minBet
                    # Do they have sufficient chips?
                    if playerBet > players[activePlayerIndex].chips:
                        print("Not enough chips")
                        continue
                    # Update the stored player bet thus far
                    playerBets[activePlayerIndex] += playerBet
                    # Update the current bet
                    currentBet = playerBets[activePlayerIndex]
                    # Not passing
                    playersPassing[activePlayerIndex] = False
                    # Update the pot
                    pot += players[activePlayerIndex].bet(playerBet)
                elif action == "LOW_BET":
                    # Calculate player bet
                    playerBet = incomingBet + players[activePlayerIndex].chips * 0.1 if players[activePlayerIndex].chips * 0.1 > self.minBet else self.minBet
                    # Do they have sufficient chips?
                    if playerBet > players[activePlayerIndex].chips:
                        print("Not enough chips")
                        continue
                    # Update the stored player bet thus far
                    playerBets[activePlayerIndex] += playerBet
                    # Update the current bet
                    currentBet = playerBets[activePlayerIndex]
                    # Not passing
                    playersPassing[activePlayerIndex] = False
                    # Update the pot
                    pot += players[activePlayerIndex].bet(playerBet)
                elif action == "MID_BET":
                    # Calculate player bet
                    playerBet = incomingBet + players[activePlayerIndex].chips * 0.4 if players[activePlayerIndex].chips * 0.4 > self.minBet else self.minBet
                    # Do they have sufficient chips?
                    if playerBet > players[activePlayerIndex].chips:
                        print("Not enough chips")
                        continue
                    # Update the stored player bet thus far
                    playerBets[activePlayerIndex] += playerBet
                    # Update the current bet
                    currentBet = playerBets[activePlayerIndex]
                    # Not passing
                    playersPassing[activePlayerIndex] = False
                    # Update the pot
                    pot += players[activePlayerIndex].bet(playerBet)
                elif action == "HGH_BET":
                    # Calculate player bet
                    playerBet = incomingBet + players[activePlayerIndex].chips * 0.7 if players[activePlayerIndex].chips * 0.7 > self.minBet else self.minBet
                    # Do they have sufficient chips?
                    if playerBet > players[activePlayerIndex].chips:
                        print("Not enough chips")
                        continue
                    # Update the stored player bet thus far
                    playerBets[activePlayerIndex] += playerBet
                    # Update the current bet
                    currentBet = playerBets[activePlayerIndex]
                    # Not passing
                    playersPassing[activePlayerIndex] = False
                    # Update the pot
                    pot += players[activePlayerIndex].bet(playerBet)
                elif action == "ALL_IN":
                    # Calculate player bet
                    playerBet = players[activePlayerIndex].chips
                    # Update the stored player bet thus far
                    playerBets[activePlayerIndex] += playerBet
                    # Update the current bet
                    if playerBets[activePlayerIndex] > currentBet:
                        currentBet = playerBets[activePlayerIndex]
                    # Passing if they have 0 chips remaining (have already all-inned)
                    playersPassing[activePlayerIndex] = False if players[activePlayerIndex].chips > 0 else True
                    # Update the pot
                    pot += players[activePlayerIndex].bet(playerBet)
                elif action == "CALL":
                    # Calculate player bet
                    playerBet = incomingBet
                    # Do they have sufficient chips?
                    if playerBet > players[activePlayerIndex].chips:
                        print("Not enough chips")
                        continue
                    # Update the stored player bet thus far
                    playerBets[activePlayerIndex] += playerBet
                    # Not passing
                    playersPassing[activePlayerIndex] = False
                    # Update the pot
                    pot += players[activePlayerIndex].bet(playerBet)
                elif action == "CHECK":
                    # Can the player check?
                    if incomingBet != 0:
                        print("You must call, raise, or fold")
                        continue
                    # Passing
                    playersPassing[activePlayerIndex] = True
                elif action == "FOLD":
                    print("You have folded")
                    # Folded
                    playersFolding[activePlayerIndex] = True
                    # Passing
                    playersPassing[activePlayerIndex] = True
                else:
                    print("Try again")
                    continue                
                # Increment turn!
                i += 1
                
                # Check Condition!
                passing = True
                for j in range(playersPassing.__len__()):
                    if playersPassing[j] == False:
                        passing = False
            
            # Handle phase change
            if phase == 1:
                community.append(deck.top())
                community.append(deck.top())
                community.append(deck.top())
            elif phase == 2 or phase == 3:
                community.append(deck.top())
            elif phase == 4:
                print("Time for the results!")
            else:
                print("SOMETHING HAS GONE WRONG WITH THE PHASES!")
                print(f"THIS WAS PHASE {phase}!!!")
            for i in range(players.__len__()):
                players[i].communityUpdate(community)
            
            # Change phase
            phase += 1

        # Check the score of each player's hand
        scores = []
        for i in range(players.__len__()):
            if playersFolding[i]:
                scores.append(0)
            else:
                scores.append(players[i].handScore())
        maxScore = -1
        winningIndex = []
        for i in range(players.__len__()):
            if scores[i] > maxScore:
                maxScore = scores[i]
                winningIndex = [i]
            elif scores[i] == maxScore:
                winningIndex.append(i)
        
        print()
        communityString = "["
        for card in community:
            communityString += f"{card}, "
        if community.__len__() > 0:
            communityString = communityString[:-2] + "]"
        else:
            communityString += "]"
        print(f"River State: {communityString}")
        print()
        print(f"Player Scores/Hands:")
        for i in range(players.__len__()):
            print(f"Player {players[i].id} score: {scores[i]}")
            print(f"\t hand: {players[i].hand()}")
        
        if winningIndex.__len__() > 1:
            print(f"The winners are:")
            for i in winningIndex:
                print(f"Player {players[i].id}")
            tieScores = []
            for i in range(players.__len__()):
                if i not in winningIndex:
                    tieScores.append(0)
                else:
                    temp = players[i].handCards
                    temp.sort(key=lambda x: x.value, reverse = True)
                    tieScores.append(temp[0].value * 10 + temp[1].value)
            
            print("Tie Breaker Hands:")
            for i in winningIndex:
                print(f"Player {players[i].id} hand: {players[i].hand()}")

            tiebreaker = -1
            tieWinningIndex = []
            for i in winningIndex:
                if tieScores[i] > tiebreaker:
                    tiebreaker = tieScores[i]
                    tieWinningIndex = [i]
                elif tieScores[i] == tiebreaker:
                    tieWinningIndex.append(i)

            winningIndex = tieWinningIndex
            if winningIndex.__len__() == 1:
                print(f"The tiebreak winner is: Player {winningIndex[0] + 1}")
            else:
                print(f"The tiebreak winners are:")
                for i in winningIndex:
                    print(f"Player {players[i].id}")
        else: 
            print(f"The winner is: Player {winningIndex[0] + 1}")
        
        print(f"The pot won is: {pot} chips!!!")

        if winningIndex.__len__() == 1:
            players[winningIndex[0]].wins(pot)
            print(f"Player {players[winningIndex[0]].id} wins {pot} chips!")
        else:
            numWinners = winningIndex.__len__()
            for i in winningIndex:
                players[winningIndex[i]].wins(pot/numWinners)
                print(f"Player {players[winningIndex[i]].id} wins {pot/numWinners} chips!")
        
        # Clean players hands
        for i in range(players.__len__()):
            players[i].handCards = []

        # Eliminate players as necessary
        temp = []
        newButtonPlayerIndex = self.buttonPlayerIndex
        for i in range(players.__len__()):
            if players[i].chips >= self.minBet:
                temp.append(players[i])
            elif i == self.buttonPlayerIndex:
                newButtonPlayerIndex += 1
        if newButtonPlayerIndex == self.buttonPlayerIndex:
            newButtonPlayerIndex += 1
        self.buttonPlayerIndex = newButtonPlayerIndex % temp.__len__()
        self.players = temp
        print()
        input("Next Round (hit enter to continue)")

        return

    def runGame(self):
        while self.players.__len__() > 1:
            self.runRound()
        
        print(f"THE WINNER IS: PLAYER {self.players[0].id}")


testGame = Poker(numPlayers = 2,startChips = 100, minBet = 2)

testGame.runGame()


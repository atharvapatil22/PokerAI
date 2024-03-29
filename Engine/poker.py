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
        # Normal Poker
        if players.__len__() > 2:
            # Small blind
            pot += players[(self.buttonPlayerIndex + 1) % players.__len__()].bet(self.minBet / 2)
            # Big blind
            pot += players[(self.buttonPlayerIndex + 2) % players.__len__()].bet(self.minBet)
            # Under the gun
            activePlayerIndex = (self.buttonPlayerIndex + 3) % players.__len__()
        # HEADS UP POKER
        else:
            # Dealer is small blind
            pot += players[(self.buttonPlayerIndex) % players.__len__()].bet(self.minBet / 2)
            # Other is big blind
            pot += players[(self.buttonPlayerIndex + 1) % players.__len__()].bet(self.minBet)
            # Dealer is under the gun
            activePlayerIndex = (self.buttonPlayerIndex) % players.__len__()

        # Deal cards
        for i in range(players.__len__() * 2):
            players[(i+1+self.buttonPlayerIndex) % players.__len__()].dealt(deck.top())
        
        # Setup state arraylists
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
            # i = activePlayerIndex
            while (not passing):
                # Table turn cycle:

                # Handle folded players
                if playersFolding[activePlayerIndex]:
                    print(f"Player {players[activePlayerIndex].id} has folded.")
                    playersPassing[activePlayerIndex] = True
                    # Increment turn!
                    activePlayerIndex += 1
                    # Handle overflow
                    activePlayerIndex = (activePlayerIndex) % players.__len__()
                    continue
                # Print player interface
                print(f"Player {players[activePlayerIndex].id}, it is your turn.")

                # REFNOTE: This sequence of code is reused elsewhere, it would be a good method for the round class
                communityString = "["
                for card in community:
                    communityString += f"{card}, "
                if community.__len__() > 0:
                    communityString = communityString[:-2] + "]"
                else:
                    communityString += "]"
                
                # Display relevant information to the user
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
                
                # REFNOTE: The handling of player actions definitely should be handled by methods.
                # A lot of the functionality is the same between them, or at least pretty similar,
                # so you can factor that out, or not it doesn't matter too much. The important thing
                # is that methods are handling each of the potential actions.
                # Also, currently actions are only accepted on the command line, perhaps a method in the
                # Player class could be used to determine what type of input should be used (command line
                # for real players, the appropriate decision making method for agent players, etc.) once
                # the class recieves it's rework.

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
                activePlayerIndex += 1
                # Handle overflow
                activePlayerIndex = (activePlayerIndex) % players.__len__()
                
                # Check Condition!
                passing = True
                # If any of the players are not passive, continue this phase
                for j in range(playersPassing.__len__()):
                    if playersPassing[j] == False:
                        passing = False
            
            # Handle phase change
            # Phase 1-->2 Preflop --> Flop
            if phase == 1:
                community.append(deck.top())
                community.append(deck.top())
                community.append(deck.top())
            # Phase 2-->3 Flop --> Turn
            # Phase 3-->4 Turn --> River
            elif phase == 2 or phase == 3:
                community.append(deck.top())
            # Phase 4-->5 River --> Scores
            elif phase == 4:
                print("Time for the results!")
            # This should never occur, the prints are for debuggging in case it does
            else:
                print("SOMETHING HAS GONE WRONG WITH THE PHASES!")
                print(f"THIS WAS PHASE {phase}!!!")

            # REFNOTE: Eventually this might become unnecessary due to the functionality
            # of checking score being planned to move to the Engine class instead of the
            # player class... but if we want the agent to be able to calculate odds of hands
            # and such, the agent would need to know the community cards, so it might not be
            # worth removing the community knowledge from the players just yet.
            
            # Update each player's knowledge of the community cards
            for i in range(players.__len__()):
                players[i].communityUpdate(community)
            
            # Change phase
            phase += 1

        # Check the score of each player's hand
        scores = []
        for i in range(players.__len__()):
            # Folding players get 0 points
            if playersFolding[i]:
                scores.append(0)
            # Scores are calculated by the player objects
            else:
                # REFNOTE: This could change to being done by the Engine, taking
                # each players 2 card hand and the community cards into account 
                scores.append(players[i].handScore())
        
        # Find winners
        maxScore = -1
        winningIndex = []
        for i in range(players.__len__()):
            if scores[i] > maxScore:
                maxScore = scores[i]
                winningIndex = [i]
            # There can be multiple Players with equal strength best hands
            elif scores[i] == maxScore:
                winningIndex.append(i)
        
        # REFNOTE: This sequence of code is reused elsewhere, it would be a good method for the round class
        communityString = "["
        for card in community:
            communityString += f"{card}, "
        if community.__len__() > 0:
            communityString = communityString[:-2] + "]"
        else:
            communityString += "]"

        # Print player scores and hands (along with community cards for context)
        print()
        print(f"River State: {communityString}")
        print()
        print(f"Player Scores/Hands:")
        for i in range(players.__len__()):
            print(f"Player {players[i].id} score: {scores[i]}")
            print(f"\t hand: {players[i].hand()}")
        
        # If there are multiple winners, tie-break by cards in hand
        if winningIndex.__len__() > 1:
            # Display information about multiple winners
            print(f"The winners are:")
            for i in winningIndex:
                print(f"Player {players[i].id}")
            
            # Identify tie-break scores
            tieScores = []
            for i in range(players.__len__()):
                # If not a winner, no tiebreak score
                if i not in winningIndex:
                    tieScores.append(0)
                # If a winner, calculate tie-break score
                else:
                    temp = players[i].handCards
                    temp.sort(key=lambda x: x.value, reverse = True)
                    # tie-break score = high card value * 10 + low card value
                    tieScores.append(temp[0].value * 10 + temp[1].value)
            
            # Display information about tie-breaker hands
            print("Tie Breaker Hands:")
            for i in winningIndex:
                print(f"Player {players[i].id} hand: {players[i].hand()}")

            # Find winners
            tiebreaker = -1
            tieWinningIndex = []
            for i in winningIndex:
                if tieScores[i] > tiebreaker:
                    tiebreaker = tieScores[i]
                    tieWinningIndex = [i]
                # There can be multiple Players with equal strength hands
                elif tieScores[i] == tiebreaker:
                    tieWinningIndex.append(i)

            # Display information about who won the tie-break
            winningIndex = tieWinningIndex
            if winningIndex.__len__() == 1:
                print(f"The tiebreak winner is: Player {winningIndex[0] + 1}")
            else:
                print(f"The tiebreak winners are:")
                for i in winningIndex:
                    print(f"Player {players[i].id}")
        else: 
            # Display information about who won the pot
            print(f"The winner is: Player {winningIndex[0] + 1}")
        
        # Display pot won
        print(f"The pot won is: {pot} chips!!!")

        # Display how much each winner won
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

        # Eliminate players as necessary, and update Dealer Button
        temp = []
        for i in range(players.__len__()):
            # If a player has remaining chips greater than or equal to the minimum bet,
            # they continue to the next round, otherwise they are eliminated
            if players[i].chips >= self.minBet:
                temp.append(players[i])
            # If the dealer is to be eliminated, move the button one spot to the right.
            elif i == self.buttonPlayerIndex:
                self.buttonPlayerIndex -= 1
        # The dealer button moves to the left
        self.buttonPlayerIndex += 1
        self.buttonPlayerIndex = self.buttonPlayerIndex % temp.__len__()

        # REFNOTE: in the Round class that is likely going to be added, the primary method
        # of the Round class used by the main poker engine class should return the updated
        # player arraylist (with updated chip counts, blank community cards and hands, etc.)
        # so that if players are eliminated, the poker engine can communicate that to the
        # next round.

        # Eliminate players in object field
        self.players = temp
        print()
        input("Next Round (hit enter to continue)")

        return

    # This is the primary method of the poker engine class
    # Running this method runs the game to completion
    def runGame(self):
        # Rounds continue until only one player is left
        # That player is the winner
        while self.players.__len__() > 1:
            self.runRound()
        
        print(f"THE WINNER IS: PLAYER {self.players[0].id}")


testGame = Poker(numPlayers = 2,startChips = 100, minBet = 2)

testGame.runGame()


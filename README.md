# PokerAI

To run the game, go to the "Engine" folder and type "py testPoker.py". Doing this will run the game with the default options, which include a Simulation Agent as player 1 and a Monte Carlo Agent as player 2. To change what agents are being played, modify the "testPoker.py" file to call the corresponding functions of the agents you want to include in a game. Make sure only two players are being added to each game; the first function called will be player 1 and the second function called will be player 2. To play the game with two real players, comment out every add agent function and make sure there are two calls to "addRealPlayer()". To play the game against an agent, make sure there is one function call to make a Real Player, and one function call to make an agent.

The default test sequence is "test_sequences7.txt" which is a 300 game test sequence with 200 rounds for each game. To modify what test sequence is being used, change the file in the call to parseFile inside of "testPoker.py" to another test sequence file. To create more test sequences, use the GenerateTestSequences.py script inside the Testing folder. This script takes in three arguments: the number of games, the number of sequences per game, and the file name. Running "py GenerateTestSequences.py 100 200 test_sequences8.txt" will create a new file called test_sequences8 with 100 games and 200 rounds per game in the current directory. 

After testPoker.py runs, it will create two output files called "p1Output.txt" and "p2Output.txt". These contain the full chip records of each player for every round in every game.

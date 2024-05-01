import sys
import random
games = sys.argv[1]
sequences_per_game = sys.argv[2]
file_name = sys.argv[3]
values = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
suits = ["Sp", "Cl", "Di", "He"]
cards = [value + " " + suit for value in values for suit in suits]


with open(file_name, "w") as f:
    for i in range(int(games)):
        sequences = []
        for _ in range(int(sequences_per_game)):
            sequences.append(random.sample(cards, 9))
        f.write(f"Game {str(i+1)} Sequences: {', '.join(map(str, sequences))}\n")

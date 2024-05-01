from enum import Enum

# Map contains scores for hands in pre-flop stage. the score is 0-100
Preflop_Handscores = {(14, 14): 99.41, (13, 13): 98.82, (12, 12): 98.22, (11, 11): 97.63, (10, 10): 97.04, (9, 9): 96.45, (8, 8): 95.86, (7, 7): 95.27, (13, 14): 92.9, (12, 14): 91.12, (11, 14): 90.53, (10, 14): 89.35, (6, 6): 91.72, (12, 13): 85.8, (11, 13): 85.21, (9, 14): 84.02, (10, 13): 82.25, (8, 14): 81.07, (5, 5): 86.39, (7, 14): 78.7, (11, 12): 77.51, (9, 13): 75.74, (10, 12): 73.96, (5, 14): 72.78, (6, 14): 72.19, (4, 14): 70.41, (4, 4): 78.11, (8, 13): 69.23, (10, 11): 68.05, (9, 12): 67.46, (3, 14): 66.27, (7, 13): 65.09, (2, 14): 64.5, (6, 13): 61.54, (8, 12): 60.36, (9, 11): 59.76, (5, 13): 57.99, (3, 3): 65.68, (4, 13): 55.62, (9, 10): 55.03, (7, 12): 53.85, (8, 11): 53.25, (3, 13): 51.48, (6, 12): 49.7, (2, 13): 48.52, (8, 10): 47.34, (5, 12): 46.15, (7, 11): 45.56, (2, 2): 54.44, (4, 12): 43.2, (8, 9): 42.6, (3, 12): 40.24, (7, 10): 40.83, (6, 11): 39.64, (2, 12): 37.28, (5, 11): 36.69, (7, 9): 35.5, (4, 11): 34.32, (6, 10): 33.73, (3, 11): 30.77, (7, 8): 31.36, (6, 9): 28.99, (2, 11): 28.4, (5, 10): 27.81, (4, 10): 26.04, (6, 8): 24.85, (5, 9): 23.08, (3, 10): 22.49, (6, 7): 21.3, (2, 10): 20.12, (5, 8): 19.53, (4, 9): 17.16, (5, 7): 16.57, (3, 9): 14.79, (5, 6): 14.2, (4, 8): 13.02, (2, 9): 11.83, (4, 7): 10.65, (4, 5): 9.47, (4, 6): 8.28, (3, 8): 7.1, (2, 8): 6.51, (3, 7): 5.33, (3, 5): 4.73, (3, 6): 3.55, (3, 4): 2.96, (2, 7): 2.37, (2, 5): 1.78, (2, 6): 1.18, (2, 4): 0.59, (2, 3): 0.2}

# the return types of Minimax.check_pairs method
class CheckPairTypes(Enum):
    THREE_KIND = 'THREE_KIND'
    TWO_PAIR = "TWO_PAIR"
    ONE_PAIR = "ONE_PAIR"
    
from enum import Enum
import sys
import time
import functools

sys.setrecursionlimit(10000500)

@functools.lru_cache(10**6)
def cache(func):
    return func

verbose=False
global_search_depth = 100
global_max_score = 200
global_round_count = 50

class Phase(Enum):
    BID = 1
    HAND = 2
    SCORE = 3


class PlayerCardPair:
    def __init__(self, player, card):
        self.player = player
        self.card = card

    def print(self):
        print(self.player, " - ",  self.card, end=" ")


def print_cards(valid_cards):
    print("[", end=" ")
    for card in valid_cards:
        card.print()
    print("]")

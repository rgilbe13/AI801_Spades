import random
from copy import deepcopy
from CommonSpades import *
from MiniMaxSearch import *
import time

def sortFunc(e):
    return e.suit, e.val

class Player():

    def __init__(self, name):
        self.name = name
        self.hand = []
        self.bet = 0
        self.tricks = 0
        self.bags = 0
        self.score = 0
        self.next_player = None

    def remove_card(self, card):
        if self.hand.count(card) == 1:
            self.hand.remove(card)
        else:
             raise Exception("Card Not Found!")
    
    def __str__(self):
        return f"{self.name}"

    def set_next_player(self, player):
        self.next_player = player

    def make_bet(self):
        pass
    
    def make_move(self):
        pass
    
    def print_hand(self):
        print("[", end=" ")
        for card in self.hand:
            card.print()
        print("]")
        print(f"Count - {len(self.hand)}")
    
    def get_valid_cards(self, opening_suit, spades_broken):
        valid_hand = []
        for card in self.hand:
            # Check if the card matches the opening suit
            if card.suit == opening_suit:
                valid_hand.append(card)
            # Allow any card if no opening suit (first turn), but avoid spades if not broken
            elif opening_suit is None and (card.suit != 0 or spades_broken):
                valid_hand.append(card)

        # If no valid cards found, player can play any card
        if len(valid_hand) == 0:
            valid_hand = deepcopy(self.hand)

        # Sort the valid hand
        valid_hand.sort(key=sortFunc)

        # Debug print to check the valid hand
        #print(f"Valid hand for player with opening_suit {opening_suit} and spades_broken {spades_broken}: {valid_hand}")

        return valid_hand

    
    
class AIPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def make_bet(self):
        self.bet = random.randint(2,5)

    def make_move(self, game, state):
        valid_hand = self.get_valid_cards(state.current_trick.opening_suit, state.spades_broken)
        selected_card = random.choice(valid_hand)
        #self.hand.remove(selected_card)
        return selected_card


class MINMAXPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def make_move(self, game, state):
        v, move = minimax_search(game, state)
        return move
    
    def make_bet(self):
        self.bet = random.randint(2, 5)



class Team:
    def __init__(self, p1, p2):
        self.members = [p1, p2]
        self.bags = 0
        self.score = 0        
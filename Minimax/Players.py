import random
from copy import deepcopy
#from CommonSpades import *
#from MiniMaxSearch import *
from MinMaxAlphaBeta import *
#from Card import *
#from MiniMaxDepthLimit import *
#from MiniMaxBreadthFirst import *
import time

def sortFunc(e):
    return e.suit, e.val

class Player():

    def __init__(self, name, team_name):
        self.name = name
        self.team_name = team_name
        self.hand = []
        self.bet = 0
        self.tricks = 0
        self.bags = 0
        self.score = 0
        self.next_player = None

        # Probability table for non-spades suits developed by Cohensius et al.
        self.probability_table = {
            0: {0: 0.997, 1: 0.966, 2: 0.817},
            1: {0: 0.994, 1: 0.942, 2: 0.733},
            2: {0: 0.990, 1: 0.907, 2: 0.624},
            3: {0: 0.983, 1: 0.855, 2: 0.489},
            4: {0: 0.970, 1: 0.779, 2: 0.350},
            5: {0: 0.948, 1: 0.678, 2: 0.212},
            6: {0: 0.915, 1: 0.544, 2: 0.095},
            7: {0: 0.857, 1: 0.381, 2: 0.025},
            8: {0: 0.774, 1: 0.214, 2: 0},
            9: {0: 0.646, 1: 0.074, 2: 0},
            10: {0: 0.462, 1: 0, 2: 0},
            11: {0: 0.227, 1: 0, 2: 0},
            12: {0: 0, 1: 0, 2: 0}
        }        

    def addTrick(self):
        self.tricks += 1

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
        nil_bet = False
        expected_tricks = self.evaluate_regular_bet()
        # if expected_tricks <= 2 and Card(0, 12) not in self.hand:
        #     nil_bet = self.evaluate_nil_bet()
        # self.bet = 0 if nil_bet else expected_tricks


    def evaluate_regular_bet(self):
        expected_tricks = 0
        for i in range(4):
            suit_arr = [card for card in self.hand if card.suit == i]
            suit_arr.reverse()
            suit_count = len(suit_arr)
            if i == 0: # Case for evaluating Spades
                high_value_spades = [card for card in suit_arr if card.val >= 9] # Only concerned with spades of val J-A
                for index, card in enumerate(high_value_spades):
                    higher_value_cards = abs(12 - card.val)
                    # The J-Q-K-A spades are each worth a trick if there are more spades in hand than number of un-owned higher-ranked spades
                    if (suit_count > higher_value_cards-index): # Subtract number of higher owned cards
                        expected_tricks+=1
                if suit_count >= 5: # Add a trick for every spade in hand over the fourth
                    expected_tricks += suit_count - 4
            else: # Case for non-Spade suits
                probabilities = self.probability_table[suit_count]
                for card in suit_arr:
                    if card.val == 12:
                        expected_tricks += probabilities[0]
                    elif card.val == 11:
                        expected_tricks += probabilities[1]
                    elif card.val == 10: 
                        expected_tricks += probabilities[2]
                    else:
                        break
        return round(expected_tricks) if round(expected_tricks) > 0 else 1

    def evaluate_nil_bet(self):
        for i in range(4):
            suit_arr = [card for card in self.hand if card.suit == i]
            suit_arr.reverse()
            last_three = suit_arr[-3:] # Gets the three lowest value cards for the given suit
            if last_three[0].val > 8: # Checks if the suit hand is 'unsafe' (Bottom 3 value cards contain J or greater)
                return False
        print('ATTEMPTING NIL')
        return True

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
    def __init__(self, name, team_name):
        super().__init__(name, team_name)

    def make_bet(self):
        #self.bet = random.randint(2,5)
        self.bet = self.evaluate_regular_bet()

    def make_move(self, game, state):
        valid_hand = self.get_valid_cards(state.current_trick.opening_suit, state.spades_broken)
        selected_card = random.choice(valid_hand)
        #self.hand.remove(selected_card)
        return selected_card


class MINMAXPlayer(Player):
    def __init__(self, name, team_name):
        super().__init__(name, team_name)

    def make_move(self, game, state):
        v, move = minimax_search(game, state)
        if verbose:
            print("Value: ", v)
        return move
    
    def make_bet(self):
        self.bet = random.randint(2, 5)


class MINMAXAlphaBetaPlayer(Player):
    def __init__(self, name, team_name):
        super().__init__(name, team_name)

    def make_move(self, game, state):
        v, move = alphabeta_search(game, state)
        if verbose:
            print("Value: ", v)
        return move
    
    def make_bet(self):
        # self.bet = random.randint(2, 5)  
        self.bet = self.evaluate_regular_bet()      


class MINMAXAlphaBetaDepthPlayer(Player):
    def __init__(self, name, team_name):
        super().__init__(name, team_name)

    def make_move(self, game, state):
        v, move = minimax_depth_limit_search(game, state)
        if verbose:
            print("Value: ", v)
        return move
    
    def make_bet(self):
        self.bet = random.randint(2, 5)    

class MINMAXAlphaBetaBredthFirstPlayer(Player):
    def __init__(self, name, team_name):
        super().__init__(name, team_name)

    def make_move(self, game, state):
        v, move = alphabeta_breadth_first_search(game, state, True)
        if verbose:
            print("Value: ", v)
        return move
    
    def make_bet(self):
        self.bet = random.randint(2, 5)    

class Team:
    def __init__(self, p1, p2):
        self.members = [p1, p2]
        self.bags = 0
        self.score = 0        
        self.tricks = 0
        self.bet = 0
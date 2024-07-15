from enum import Enum
import sys
import functools

sys.setrecursionlimit(10000500)

@functools.lru_cache(10**6)
def cache(func):
    return func

verbose=True

class Phase(Enum):
    BID = 1
    HAND = 2
    SCORE = 3


class PlayerCardPair:
    def __init__(self, player, card):
        self.player = player
        self.card = card

    def print(self):
        print(f"{self.player.name} --- {self.card.print()}", end=" ")
suit_dict = {0: '♠', 1: '♣', 2: '♥', 3: '♦'}
val_dict = {0: '2', 1: '3', 2: '4', 3: '5',
        4: '6', 5: '7', 6: '8', 7: '9',
        8: '10', 9: 'J', 10: 'Q', 11: 'K',
        12: 'A'}


class Card:
    
    def __init__(self,suit,val):
        self.suit = suit
        self.val = val

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.suit == other.suit and self.val == other.val
    
    def __str__(self):
        return f"{val_dict[self.val]}-{suit_dict[self.suit]}"
        
    def print(self):
        print(f"{val_dict[self.val]}-{suit_dict[self.suit]}", end=" ")
import random
from copy import deepcopy
from CommonSpades import *
from MiniMaxSearch import *

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

    def print(self):
        print(f"{self.name}", end="")
        
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
        self.hand.remove(selected_card)
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
import math

infinity = math.inf

def minimax_search(game, state):
    """Search game tree to determine best move; return (value, move) pair."""

    player = state.current_player
 

    def max_value(state):

        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a))
            if v2 > v:
                v, move = v2, a
        print('Val', v, 'Move:', move[1].print())
        return v, move

    def min_value(state):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a))
            if v2 < v:
                v, move = v2, a
        print('Val', v, 'Move:', move[1].print())                
        return v, move

    return max_value(state)
from collections import namedtuple, Counter, defaultdict
import random


import numpy as np
from copy import deepcopy
from CommonSpades import *
from Card import *
from Players import *

class Trick:
    def __init__(self):
        self.cards = []
        self.opening_suit = None
        self.winning_player = None
    
    def evaluate_trick(self):
        highest_val = 0
        for pair in self.cards:
            if pair.card.suit == 0 and self.opening_suit != 0:
                self.opening_suit = 0
                highest_val = pair.card.val
                self.winning_player = pair.player
            elif pair.card.suit == self.opening_suit and pair.card.val >= highest_val:
                highest_val = pair.card.val
                self.winning_player = pair.player
        
        return self.winning_player
    
    def add_card(self, player, card):
        if type(card) is not Card:
            raise Exception("Not a card")
        if self.opening_suit == None:
            self.opening_suit = card.suit
        self.cards.append(PlayerCardPair(player, card))

    def print(self):
        print("[", end=" ")
        for pair in self.cards:
            pair.print()
        print("]")


class GameState():
    def __init__(self, starting_player):
        self.current_trick = Trick()
        self.trick_history = []
        self.current_player = starting_player
        self.dealer = None
        self.phase = Phase.BID
        self.spades_broken = False
        self.cards_laid = 0

    def new(self):
        return deepcopy(self)

    def lay_card(self, card):
        self.cards_laid += 1
        self.current_trick.add_card(self.current_player, card)
        self.update_current_player(self.current_player.next_player)
        if len(self.current_trick.cards) == 4:
            if(verbose):
                self.current_trick.print()
            self.end_round()

    def end_round(self):
        #self.update_current_player(self.current_trick.evaluate_trick())
        
        if not self.spades_broken:
            for pair in self.current_trick.cards:
                if pair.card.suit == 0:
                    self.spades_broken = True

        self.trick_history.append(self.current_trick)
        self.current_trick = Trick()


    def update_current_player(self, player):
        self.current_player = player

    def update_dealer(self, dealer):
        self.dealer = dealer

    def update_phase(self, phase):
        self.phase = phase

    def to_move(self):
        return self.current_player
    
    def actions(self):
            valid_cards = self.current_player.get_valid_cards(self.current_trick.opening_suit, self.spades_broken)
            return valid_cards
        
class Spades():
    def __init__(self, starting_player):
        self.initial = GameState(starting_player)

    def actions(self, state):
        return state.actions()

    def result(self, state, action):
        #state = state.new()
        state.lay_card(action)
        
        return state

    def utility(self, state, player):
        return 1

    def is_terminal(self, state):
        return state.cards_laid == 52
        
    def display(self, state): 
        print(state)

    def build_deck(self):
        deck = []
        for s in range(4):
            for v in range(13):
                card = Card(s, v)
                if card not in deck:
                    deck.append(card)
        return deck
    
    def deal_hand(self, state):
        deck = self.build_deck()
        random.shuffle(deck)
        for _ in range(4):
            for _ in range(13):
                card = deck.pop()
                state.current_player.hand.append(card)
            state.update_current_player(state.current_player.next_player)

    def new_game(self, state):
        self.deal_hand(state) 

from Game import *

p1 = AIPlayer("Tom")
p2 = AIPlayer("Bruce")
p3 = AIPlayer("Randy")
p4 = MINMAXPlayer("Rex")

p1.set_next_player(p2)
p2.set_next_player(p3)
p3.set_next_player(p4)
p4.set_next_player(p1)

def play_game(game):
    state = game.initial
    game.new_game(state)

    for _ in range(4):
        state.current_player.make_bet()
        state.update_current_player(state.current_player.next_player)

    while not game.is_terminal(state):
        player = state.current_player
        if verbose:
            print(f"Player to move: {player.print()}")
        move = player.make_move(game, state)
        state = game.result(state, move)
        if verbose: 
            print('Player', player, 'move:', move)
            print(state)
    return state

play_game(Spades(p1))from enum import Enum
import sys
import time
import functools

sys.setrecursionlimit(10000500)

@functools.lru_cache(10**6)
def cache(func):
    return func

verbose=True

class Phase(Enum):
    BID = 1
    HAND = 2
    SCORE = 3


class PlayerCardPair:
    def __init__(self, player, card):
        self.player = player
        self.card = card

    def print(self):
        print(f"{self.player.name} --- {self.card.print()}", end=" ")
suit_dict = {0: '♠', 1: '♣', 2: '♥', 3: '♦'}
val_dict = {0: '2', 1: '3', 2: '4', 3: '5',
        4: '6', 5: '7', 6: '8', 7: '9',
        8: '10', 9: 'J', 10: 'Q', 11: 'K',
        12: 'A'}


class Card:
    
    def __init__(self,suit,val):
        self.suit = suit
        self.val = val

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.suit == other.suit and self.val == other.val
    
    def __str__(self):
        return f"{val_dict[self.val]}-{suit_dict[self.suit]}"
        
    def print(self):
        print(f"{val_dict[self.val]}-{suit_dict[self.suit]}", end=" ")
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
        self.hand.remove(selected_card)
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
import math
import time
infinity = math.inf

def minimax_search(game, state):
    def max_value(state):
        if game.is_terminal(state):
            return game.utility(state, state.current_player), None
        v, move = -infinity, None
        for a in game.actions(state):
            time.sleep(1)
            v2, _ = min_value(game.result(state, a))
            if v2 > v:
                v, move = v2, a
        print('Val', v, 'Move:', move.print())
        return v, move

    def min_value(state):
        if game.is_terminal(state):
            return game.utility(state, state.current_player), None
        v, move = +infinity, None
        for a in game.actions(state):
            time.sleep(1)
            v2, _ = max_value(game.result(state, a))
            if v2 < v:
                v, move = v2, a
        print('Val', v, 'Move:', move.print())                
        return v, move

    return max_value(state)
from collections import namedtuple, Counter, defaultdict
import random


import numpy as np
from copy import deepcopy
from CommonSpades import *
from Card import *
from Players import *

class Trick:
    def __init__(self):
        self.cards = []
        self.opening_suit = None
        self.winning_player = None
    
    def evaluate_trick(self):
        highest_val = 0
        for pair in self.cards:
            if pair.card.suit == 0 and self.opening_suit != 0:
                self.opening_suit = 0
                highest_val = pair.card.val
                self.winning_player = pair.player
            elif pair.card.suit == self.opening_suit and pair.card.val >= highest_val:
                highest_val = pair.card.val
                self.winning_player = pair.player
        
        return self.winning_player
    
    def add_card(self, player, card):
        if type(card) is not Card:
            raise Exception("Not a card")
        if self.opening_suit == None:
            self.opening_suit = card.suit
        self.cards.append(PlayerCardPair(player, card))

    def print(self):
        print("[", end=" ")
        for pair in self.cards:
            pair.print()
        print("]")


class GameState():
    def __init__(self, starting_player):
        self.current_trick = Trick()
        self.trick_history = []
        self.current_player = starting_player
        self.dealer = None
        self.phase = Phase.BID
        self.spades_broken = False
        self.cards_laid = 0

    def new(self):
        return deepcopy(self)

    def lay_card(self, card):
        self.cards_laid += 1
        self.current_trick.add_card(self.current_player, card)
        
        if len(self.current_trick.cards) == 4:
            if(verbose):
                self.current_trick.print()
            self.end_round()
        else:
            self.update_current_player(self.current_player.next_player)

        if verbose:
            print("State: lay_card(): Player changed to: ", self.current_player, " Card added: ", card)            

    def end_round(self):
        self.update_current_player(self.current_trick.evaluate_trick())
        
        if not self.spades_broken:
            for pair in self.current_trick.cards:
                if pair.card.suit == 0:
                    self.spades_broken = True

        self.trick_history.append(self.current_trick)
        self.current_trick = Trick()


    def update_current_player(self, player):
        self.current_player = player

    def update_dealer(self, dealer):
        self.dealer = dealer

    def update_phase(self, phase):
        self.phase = phase

    def to_move(self):
        return self.current_player
    
    def actions(self):
            valid_cards = self.current_player.get_valid_cards(self.current_trick.opening_suit, self.spades_broken)
            if verbose:
                print("actions() called: ", valid_cards)
            return valid_cards
        
class Spades():
    def __init__(self, starting_player):
        self.initial = GameState(starting_player)

    def actions(self, state):
        return state.actions()

    def result(self, state, action):
        #state = state.new()
        state.lay_card(action)
        
        return state

    def utility(self, state, player):
        return 1

    def is_terminal(self, state):
        if verbose:
            print("Spades: is_terminal(): ", state.cards_laid)
        if state.cards_laid == 52:
            return True
        else:
            return False
        
    def display(self, state): 
        print(state)

    def build_deck(self):
        deck = []
        for s in range(4):
            for v in range(13):
                card = Card(s, v)
                if card not in deck:
                    deck.append(card)
        return deck
    
    def deal_hand(self, state):
        deck = self.build_deck()
        random.shuffle(deck)
        for _ in range(4):
            for _ in range(13):
                card = deck.pop()
                state.current_player.hand.append(card)
            state.update_current_player(state.current_player.next_player)

    def new_game(self, state):
        self.deal_hand(state) 

from Game import *

p1 = AIPlayer("Tom")
p2 = AIPlayer("Bruce")
p3 = AIPlayer("Randy")
p4 = MINMAXPlayer("Rex")

p1.set_next_player(p2)
p2.set_next_player(p3)
p3.set_next_player(p4)
p4.set_next_player(p1)

def play_game(game):
    state = game.initial
    game.new_game(state)

    for _ in range(4):
        state.current_player.make_bet()
        state.update_current_player(state.current_player.next_player)

    while not game.is_terminal(state):
        player = state.current_player
        
        if verbose:
            print('Player to move: ', player)
        
        move = player.make_move(game, state)
        
        if verbose: 
            print('Move:', move)
            time.sleep(2)

        state = game.result(state, move)

play_game(Spades(p1))from enum import Enum
import sys
import time
import functools

sys.setrecursionlimit(10000500)

@functools.lru_cache(10**6)
def cache(func):
    return func

verbose=True

class Phase(Enum):
    BID = 1
    HAND = 2
    SCORE = 3


class PlayerCardPair:
    def __init__(self, player, card):
        self.player = player
        self.card = card

    def print(self):
        print(f"{self.player.name} --- {self.card.print()}", end=" ")
suit_dict = {0: '♠', 1: '♣', 2: '♥', 3: '♦'}
val_dict = {0: '2', 1: '3', 2: '4', 3: '5',
        4: '6', 5: '7', 6: '8', 7: '9',
        8: '10', 9: 'J', 10: 'Q', 11: 'K',
        12: 'A'}


class Card:
    
    def __init__(self,suit,val):
        self.suit = suit
        self.val = val

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.suit == other.suit and self.val == other.val
    
    def __str__(self):
        return f"{val_dict[self.val]}-{suit_dict[self.suit]}"
        
    def print(self):
        print(f"{val_dict[self.val]}-{suit_dict[self.suit]}", end=" ")
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
        self.hand.remove(selected_card)
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
import math
import time
infinity = math.inf

def minimax_search(game, state):
    def max_value(state):
        if game.is_terminal(state):
            return game.utility(state, state.current_player), None
        v, move = -infinity, None
        for a in game.actions(state):
            time.sleep(1)
            v2, _ = min_value(game.result(state, a))
            if v2 > v:
                v, move = v2, a
        print('Val', v, 'Move:', move.print())
        return v, move

    def min_value(state):
        if game.is_terminal(state):
            return game.utility(state, state.current_player), None
        v, move = +infinity, None
        for a in game.actions(state):
            time.sleep(1)
            v2, _ = max_value(game.result(state, a))
            if v2 < v:
                v, move = v2, a
        print('Val', v, 'Move:', move.print())                
        return v, move

    return max_value(state)
from collections import namedtuple, Counter, defaultdict
import random


import numpy as np
from copy import deepcopy
from CommonSpades import *
from Card import *
from Players import *

class Trick:
    def __init__(self):
        self.cards = []
        self.opening_suit = None
        self.winning_player = None
    
    def evaluate_trick(self):
        highest_val = 0
        for pair in self.cards:
            if pair.card.suit == 0 and self.opening_suit != 0:
                self.opening_suit = 0
                highest_val = pair.card.val
                self.winning_player = pair.player
            elif pair.card.suit == self.opening_suit and pair.card.val >= highest_val:
                highest_val = pair.card.val
                self.winning_player = pair.player
        
        return self.winning_player
    
    def add_card(self, player, card):
        if type(card) is not Card:
            raise Exception("Not a card")
        if self.opening_suit == None:
            self.opening_suit = card.suit
        self.cards.append(PlayerCardPair(player, card))

    def print(self):
        print("[", end=" ")
        for pair in self.cards:
            pair.print()
        print("]")


class GameState():
    def __init__(self, starting_player):
        self.current_trick = Trick()
        self.trick_history = []
        self.current_player = starting_player
        self.dealer = None
        self.phase = Phase.BID
        self.spades_broken = False
        self.cards_laid = 0

    def new(self):
        return deepcopy(self)

    def lay_card(self, card):
        self.cards_laid += 1
        self.current_trick.add_card(self.current_player, card)
        
        if len(self.current_trick.cards) == 4:
            if(verbose):
                self.current_trick.print()
            self.end_round()
        else:
            self.update_current_player(self.current_player.next_player)

        if verbose:
            print("State: lay_card(): Player changed to: ", self.current_player, " Card added: ", card)            

    def end_round(self):
        self.update_current_player(self.current_trick.evaluate_trick())
        
        if not self.spades_broken:
            for pair in self.current_trick.cards:
                if pair.card.suit == 0:
                    self.spades_broken = True

        self.trick_history.append(self.current_trick)
        self.current_trick = Trick()


    def update_current_player(self, player):
        self.current_player = player

    def update_dealer(self, dealer):
        self.dealer = dealer

    def update_phase(self, phase):
        self.phase = phase

    def to_move(self):
        return self.current_player
    
    def actions(self):
            valid_cards = self.current_player.get_valid_cards(self.current_trick.opening_suit, self.spades_broken)
            if verbose:
                print("actions() called: ", valid_cards)
            return valid_cards
        
class Spades():
    def __init__(self, starting_player):
        self.initial = GameState(starting_player)

    def actions(self, state):
        return state.actions()

    def result(self, state, action):
        #state = state.new()
        state.lay_card(action)
        
        return state

    def utility(self, state, player):
        return 1

    def is_terminal(self, state):
        if verbose:
            print("Spades: is_terminal(): ", state.cards_laid)
        if state.cards_laid == 52:
            return True
        else:
            return False
        
    def display(self, state): 
        print(state)

    def build_deck(self):
        deck = []
        for s in range(4):
            for v in range(13):
                card = Card(s, v)
                if card not in deck:
                    deck.append(card)
        return deck
    
    def deal_hand(self, state):
        deck = self.build_deck()
        random.shuffle(deck)
        for _ in range(4):
            for _ in range(13):
                card = deck.pop()
                state.current_player.hand.append(card)
            state.update_current_player(state.current_player.next_player)

    def new_game(self, state):
        self.deal_hand(state) 

from Game import *

p1 = AIPlayer("Tom")
p2 = AIPlayer("Bruce")
p3 = AIPlayer("Randy")
p4 = MINMAXPlayer("Rex")

p1.set_next_player(p2)
p2.set_next_player(p3)
p3.set_next_player(p4)
p4.set_next_player(p1)

def play_game(game):
    state = game.initial
    game.new_game(state)

    for _ in range(4):
        state.current_player.make_bet()
        state.update_current_player(state.current_player.next_player)

    while not game.is_terminal(state):
        player = state.current_player
        
        if verbose:
            print('Player to move: ', player)
        
        move = player.make_move(game, state)
        
        if verbose: 
            print('Move:', move)
            time.sleep(2)

        state = game.result(state, move)

play_game(Spades(p1))
from collections import namedtuple, Counter, defaultdict
import random
import math
import functools
import numpy as np
from copy import deepcopy
from enum import Enum

@functools.lru_cache(10**6)
def cache(func):
    return func

class Phase(Enum):
    BID = 1
    HAND = 2
    SCORE = 3

suit_dict = {0: '♠', 1: '♣', 2: '♥', 3: '♦'}
val_dict = {0: '2', 1: '3', 2: '4', 3: '5',
        4: '6', 5: '7', 6: '8', 7: '9',
        8: '10', 9: 'J', 10: 'Q', 11: 'K',
        12: 'A'}

def sortFunc(e):
    return e.suit, e.val

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
        print(f"{val_dict[self.val]}-{suit_dict[self.suit]}")
        
class PlayerCardPair:
    def __init__(self, player, card):
        self.player = player
        self.card = card


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
    
    def lay_card(self, player, card):
        if self.opening_suit == None:
            self.opening_suit = card.suit
        self.cards.append(PlayerCardPair(player, card))

    
class Team:
    def __init__(self, p1, p2):
        self.members = [p1, p2]
        self.bags = 0
        self.score = 0
	        
class Player():

    def __init__(self):
        self.hand = []
        self.bet = 0
        self.tricks = 0
        self.bags = 0
        self.score = 0
        self.next_player = None

    def set_next_player(self, player):
        self.next_player = player

    def make_bet(self):
        pass
    
    def make_move(self):
        pass
    
    def print_hand(self):
        print("[", end=" ")
        for card in self.hand:
            print(f"{val_dict[card.val]}-{suit_dict[card.suit]}" , end = " ")
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
    def __init__(self):
        super().__init__()

    def make_bet(self):
        self.bet = random.randint(2,5)

    def make_move(self, game, state):
        valid_hand = self.get_valid_cards(state.current_trick.opening_suit, state.spades_broken)
        selected_card = random.choice(valid_hand)
        self.hand.remove(selected_card)
        return (Phase.HAND, selected_card)


class MINMAXPlayer(Player):
    def make_move(self, game, state):
        v, move = minimax_search(game, state)
        return (Phase.HAND, move) if move else (Phase.BID, None)  # Ensure the return is a tuple (phase, move)
    
    def make_bet(self):
        self.bet = random.randint(2, 5)

class Game:
    def actions(self, state):
        """Return a collection of the allowable moves from this state."""
        raise NotImplementedError

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        raise NotImplementedError

    def is_terminal(self, state):
        """Return True if this is a final state for the game."""
        return not self.actions(state)
    
    def utility(self, state, player):
        """Return the value of this final state to player."""
        raise NotImplementedError
        

def play_game(game, verbose=False):
    state = game.initial
    game.new_game(state)
    while not game.is_terminal(state):
        player = state.current_player
        move = player.make_move(game, state)
        state = game.result(state, move)
        if verbose: 
            print('Player', player, 'move:', move)
            print(state)
    return state

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
        return v, move

    def min_value(state):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a))
            if v2 < v:
                v, move = v2, a
        return v, move

    return max_value(state)

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
        self.current_trick.cards.append(PlayerCardPair(self.current_player, card))
        self.update_current_player(self.current_player.next_player)
        if len(self.current_trick.cards) == 4:
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
        if self.phase == Phase.BID:
            return [(Phase.BID, "")]
        else:
            valid_cards = self.current_player.get_valid_cards(self.current_trick.opening_suit, self.spades_broken)
            return [(Phase.HAND, card) for card in valid_cards]
        
class Spades(Game):
    def __init__(self, starting_player):
        self.initial = GameState(starting_player)

    def actions(self, state):
        return state.actions()

    def result(self, state, action):
        state = state.new()
        phase, card = action
        if phase == Phase.BID:
            for _ in range(4):
                state.current_player.make_bet()
                state.update_current_player(state.current_player.next_player)
            state.update_phase(Phase.HAND)
        else:
            state.lay_card(card)
        
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


def random_player(game, state): return random.choice(list(game.actions(state)))

def player(search_algorithm):
    return lambda game, state: search_algorithm(game, state)[1]

p1 = AIPlayer()
p2 = AIPlayer()
p3 = AIPlayer()
p4 = MINMAXPlayer()

p1.set_next_player(p2)
p2.set_next_player(p3)
p3.set_next_player(p4)
p4.set_next_player(p1)

play_game(Spades(p1), verbose=True)

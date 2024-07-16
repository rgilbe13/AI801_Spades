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
        if verbose:
            print("Return deepcopy")
        return deepcopy(self)

    def lay_card(self, card):
        self.cards_laid += 1
        self.current_trick.add_card(self.current_player, card)
        self.current_player.remove_card(card)
        
        if not self.spades_broken:
            for pair in self.current_trick.cards:
                if pair.card.suit == 0:
                    self.spades_broken = True
                    if verbose:
                        print("Spades Broken")

        if verbose:
            time.sleep(2)
            print(self.current_player, " played ", card)
            self.current_trick.print()                           

        if len(self.current_trick.cards) == 4:
            self.end_round()
        else:
            self.update_current_player(self.current_player.next_player)       

    def end_round(self):
        self.update_current_player(self.current_trick.evaluate_trick())
        self.trick_history.append(self.current_trick)
        self.current_trick = Trick()
        if verbose:
            time.sleep(1)
            print(self.current_player, "is the winner")

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
                print(self.current_player, " can play...")
                print_cards(valid_cards)
                time.sleep(1)
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
        print("Cards Laid: ", state.cards_laid)
        print("Is Terminal: ", state.cards_laid == 52)
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

from enum import Enum
import sys
import time
import functools

sys.setrecursionlimit(10000500)

@functools.lru_cache(10**6)
def cache(func):
    return func

verbose=False

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
from Card import *
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
                for index, card in enumerate(suit_arr):
                    higher_cards = abs(card.val - 12)
                    # A spade is worth a trick if it has more spades in hand than number of un-owned higher-ranked spades
                    if (suit_count > higher_cards-index): 
                        expected_tricks+=1
                if suit_count >= 5: # Adds a bet for every spade in hand after the fifth
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
        return round(expected_tricks)

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

    # def make_bet(self):
    #     self.bet = random.randint(2,5)

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
    
    # def make_bet(self):
    #     self.bet = random.randint(2, 5)


class Team:
    def __init__(self, p1, p2):
        self.members = [p1, p2]
        self.bags = 0
        self.score = 0        
        self.tricks = 0
        self.bet = 0
import math
import time
infinity = math.inf

search_depth = 0

def minimax_search(game, state):
    global search_depth

    
    def max_value(state):
        global search_depth
        search_depth += 1
        #time.sleep(2)
        if game.is_terminal(state) or search_depth > 3000:
            return game.utility(state, state.current_player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a))
            if v2 > v:
                v, move = v2, a
        return v, move

    def min_value(state):
        global search_depth
        search_depth += 1
        #time.sleep(2)
        if game.is_terminal(state) or search_depth > 3000:
            return game.utility(state, state.current_player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a))
            if v2 < v:
                v, move = v2, a
        return v, move
    search_depth = 0
    #state.determinize()
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
    def __init__(self, dealer):
        self.current_trick = Trick()
        self.trick_history = []
        self.dealer = dealer
        self.current_player = self.dealer.next_player
        self.spades_broken = False
        self.cards_laid = 0
        self.team_mode = False
        self.teams = []
        self.rounds = 1
        starting_player = self.current_player
        if starting_player.team_name != "":
            self.team_mode = True
            teams = {}
            teams[starting_player.team_name] = [starting_player]
            while starting_player.next_player != self.current_player:
                starting_player = starting_player.next_player
                if teams.get(starting_player.team_name) == None:
                    teams[starting_player.team_name] = [starting_player]
                else:
                    teams[starting_player.team_name].append(starting_player)

            for t in teams.values():
                self.teams.append(Team(t[0], t[1]))


    def new(self):
        return deepcopy(self)
    
    def determinize(self):
        op1 = self.current_player.next_player
        par = op1.next_player
        op2 = par.next_player
        op1_cnt = len(op1.hand)
        par_cnt = len(par.hand)
        op2_cnt = len(op2.hand)
        unseen_cards = []
        unseen_cards.extend(op1.hand)
        unseen_cards.extend(par.hand)
        unseen_cards.extend(op2.hand)
        random.shuffle(unseen_cards)
        op1.hand.extend(unseen_cards[0:op1_cnt])
        par.hand.extend(unseen_cards[op1_cnt:par_cnt])
        op2.hand.extend(unseen_cards[op1_cnt + par_cnt - 1:op2_cnt])

        # count = 1
        # for c in unseen_cards:
        #     if count%3 == 0:
        #         op1.append(c)
        #     if count%3 == 1:
        #         par.append(c)
        #     if count%3 == 2:
        #         op2.append(c)


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
            #time.sleep(4)
            print(self.current_player, " played ", card)
            self.current_trick.print()                           

        if len(self.current_trick.cards) == 4:
            self.end_hand()
        else:
            self.update_current_player(self.current_player.next_player)       

    def end_hand(self):
        self.update_current_player(self.current_trick.evaluate_trick())
        self.current_player.addTrick()
        self.trick_history.append(self.current_trick)
        self.current_trick = Trick()
        if verbose:
            print(self.current_player, "is the winner")

        if self.cards_laid == 52:
            self.end_round()

    def end_round(self):
        self.assign_score_and_bags() # Tallys points at the end of a round
        #self.print_scores()
        is_winner = self.check_for_winner(self.teams) # if self.team_mode else self.check_for_winner(self.players)
        if not is_winner:
            self.new_game()


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
            return valid_cards
    

    def build_deck(self):
        deck = []
        for s in range(4):
            for v in range(13):
                card = Card(s, v)
                if card not in deck:
                    deck.append(card)
        return deck
    
    def deal_hand(self):
        deck = self.build_deck()
        random.shuffle(deck)
        for _ in range(4):
            for _ in range(13):
                card = deck.pop()
                self.current_player.hand.append(card)
            self.update_current_player(self.current_player.next_player)

    def new_game(self):
        self.current_trick = Trick()
        self.trick_history = []
        self.dealer = self.dealer.next_player
        self.current_player = self.dealer.next_player
        self.spades_broken = False
        self.cards_laid = 0
        self.rounds += 1     
        self.deal_hand()
        for _ in range(4):
            self.current_player.make_bet()
            self.update_current_player(self.current_player.next_player)        

    def get_player_score_and_bags(self, bet, tricks):

        if bet == 0:
            score, bags = self.check_nil_bet(tricks)
        else:
            score, bags = self.get_round_score(bet, tricks)
        return score, bags
    
    def get_round_score(self, bet, tricks):

        score = -bet*10 if tricks < bet else bet*10
        bags = tricks-bet if tricks > bet else 0 # Adds bags to player total if bet was exceeded
        return score, bags
    
    def check_nil_bet(self, tricks):

        if tricks == 0:
            score = 100
            bags = 0
        else:
            score = -100
            bags = tricks
        return score, bags

    def assign_score_and_bags(self):
 
        if self.team_mode: # Case if playing with teams
            for team in self.teams:
                for player in team.members: # Adds each team members score and bag sum to the team score and bag count
                    if player.bet == 0:
                        player_round_totals = self.get_player_score_and_bags(player.bet, player.tricks)
                        team.score += player_round_totals[0] # Round Score
                        team.bags += player_round_totals[1] # Round Bags
                    else:
                        team.tricks += player.tricks
                        team.bet += player.bet
                round_totals = self.get_round_score(team.bet, team.tricks)
                team.score += round_totals[0]
                team.bags += round_totals[1]
                if team.bags >= 10: # Check for bag penalty
                    team.score -= 100
                    team.bags -= 10
        else: # Case if playing individually
            for player in self.players:
                round_totals = self.get_player_score_and_bags(player.bet, player.tricks)
                player.score += round_totals[0] # Round Score
                player.bags += round_totals[1] # Round Bags
                if player.bags >= 10:
                    player.score -= 100
                    player.bags -= 10
    
    def check_for_winner(self, player_array):

        is_winner = False
        for p in player_array:
            if p.score > 500:
                is_winner = True
                break
        return is_winner

    def print_scores(self):
        if self.team_mode:
            for t in self.teams:
                print(t.score,"(",t.bags,")")
        # else:
        #     for p in self.players:
        #         print(p.score,"(",p.bags,")")            
        
class Spades():
    def __init__(self):
        pass

    def actions(self, state):
        return state.actions()

    def result(self, state, action):
        state = state.new()
        state.lay_card(action)
        
        return state

    def utility(self, state, player):
        team = None

        for t in state.teams:
            for member in t.members:
                if player == member:
                    team = t

        player = team.members[0]
        partner = team.members[1]

        team_bet = (player.bet + partner.bet)

        remaining_cards = []
        remaining_cards.extend(player.hand)
        remaining_cards.extend(partner.hand)

        high_card_points = sum([4 if card.val == 12 else 3 if card.val == 11 else 2 if card.val == 10 else 1 if card.val == 9 else 0 for card in remaining_cards])
        expected_tricks = high_card_points // 4


        spades_count = sum(1 for card in remaining_cards if card.suit == 0)
        distribution_factor = spades_count - (13 / 4) 
        expected_tricks += distribution_factor * 0.5
        
        lead_control_points = sum([1 for card in remaining_cards if card.val in [12, 11]])
        
        bid_difference = abs(player.tricks - player.bet) + abs(partner.tricks - partner.bet)
        
        heuristic_value = (player.tricks + partner.tricks) + expected_tricks + lead_control_points - bid_difference
    
        return heuristic_value        

        return 1

    def is_terminal(self, state):
        #print("Cards Laid: ", state.cards_laid)
        #print("Is Terminal: ", state.cards_laid == 52)
        if state.cards_laid == 52:
            return True
        else:
            return False
        
    def display(self, state): 
        print(state)

from Game import *

p1 = AIPlayer("Tom", "Donkey")
p2 = AIPlayer("Bruce", "Elephant")
p3 = AIPlayer("Randy", "Donkey")
p4 = MINMAXPlayer("Rex", "Elephant")

p1.set_next_player(p2)
p2.set_next_player(p3)
p3.set_next_player(p4)
p4.set_next_player(p1)

game = Spades()
state = GameState(p1)
state.deal_hand()


while state.teams[0].score < 500 and state.teams[1].score < 500:

    player = state.current_player
    
    move = player.make_move(game, state)

    print(player," played ", move)

    state = game.result(state, move)

print("Rounds: ", state.rounds)
print("Team: ", state.teams[0].members[0].name, "/", state.teams[0].members[1].name, " - Score: ", state.teams[0].score)
print("Team: ", state.teams[1].members[0].name, "/", state.teams[1].members[1].name, " - Score: ", state.teams[1].score)
print("end")
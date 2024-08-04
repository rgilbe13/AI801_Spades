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
        self.rounds = 0
        self.time = 0
        self.value = 0
        self.best_play = None
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


    def end_round(self):
        self.assign_score_and_bags() # Tallys points at the end of a round
        #self.print_scores()
        #is_winner = self.check_for_winner(self.teams) # if self.team_mode else self.check_for_winner(self.players)
        #if not is_winner:
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
            self.current_player.tricks = 0
            self.current_player.bags = 0
            self.update_current_player(self.current_player.next_player)        

    def get_player_score_and_bags(self, bet, tricks):
        return self.get_round_score(bet, tricks)
    
    def get_round_score(self, bet, tricks):

        score = -bet*10 if tricks < bet else bet*10
        bags = tricks-bet if tricks > bet else 0 # Adds bags to player total if bet was exceeded
        return score, bags
    
    def assign_score_and_bags(self):
        for team in self.teams:
            for player in team.members: # Adds each team members score and bag sum to the team score and bag count
                team.tricks += player.tricks
                team.bet += player.bet

            round_totals = self.get_round_score(team.bet, team.tricks)
            team.score += round_totals[0]
            team.bags += round_totals[1]
            if team.bags >= 10: # Check for bag penalty
                team.score -= 100
                team.bags -= 10
    
    def check_for_winner(self, player_array):

        is_winner = False
        for p in player_array:
            if p.score > global_max_score:
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
        
        #heuristic_value = (player.tricks + partner.tricks) + expected_tricks + lead_control_points - bid_difference
        total_tricks = player.tricks + partner.tricks + expected_tricks
        if total_tricks > team_bet:
            heuristic_value =  13 - abs((team_bet - total_tricks) // 4)
        else:
            heuristic_value =  13 - abs(team_bet - total_tricks)

        if verbose:
            print("Heuristic: ", heuristic_value)
    
        return heuristic_value        


    def is_terminal(self, state):
        if state.cards_laid == 52:
            return True
        else:
            return False
        
    def display(self, state): 
        print(state)

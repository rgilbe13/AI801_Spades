import random
import numpy as np
import math
from copy import deepcopy
from enum import Enum

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
    
    def print(self):
        print(f"{val_dict[self.val]}-{suit_dict[self.suit]}")
        

class Trick:
    def __init__(self):
        self.cards = [None for i in range(4)]
        self.opening_suit = None
        self.spades_broken = False
        self.winning_player_index = 0
    
    def evaluate_trick(self):
        highest_val = 0
        for index, card in enumerate(self.cards):
            if card.suit == 0 and self.opening_suit != 0:
                self.opening_suit = 0
                highest_val = card.val
                self.winning_player_index = index
            elif card.suit == self.opening_suit and card.val >= highest_val: # Checks if same suit card is the highest value
                highest_val = card.val
                self.winning_player_index = index
        
        return self.winning_player_index
    
class Team:
    def __init__(self, p1, p2):
        self.members = [p1, p2]
        self.bags = 0
        self.score = 0
	        
class Player():

    def __init__(self, index):
        self.hand = []
        self.legal_moves = []
        self.bet = 0
        self.tricks = 0
        self.bags = 0
        self.score = 0
        self.index = index

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
            # Returns hand of cards that match first played suit (or all but spades if first turn)
            if (card.suit == opening_suit or (opening_suit is None and card.suit != 0) or (opening_suit is None and spades_broken)):
                valid_hand.append(card)
        if len(valid_hand) == 0: # Returns total hand if player can't match played suit
            valid_hand = deepcopy(self.hand)
        valid_hand.sort(key=sortFunc)
        return valid_hand
    
    
class AIPlayer(Player):
    def __init__(self, index):
        super().__init__(index)

    def make_bet(self):
        self.bet = random.randint(2,5)

    def make_move(self, trick):
        valid_hand = self.get_valid_cards(trick.opening_suit, trick.spades_broken)
        selected_card = random.choice(valid_hand)
        self.hand.remove(selected_card)
        return selected_card


class MINMAXPlayer(Player):
    def make_move(self, game, state):
        return minimax_search(game, state)
    
    def make_bet(self):
        self.bet = random.randint(2,5)    

class GameState():
    def __init__(self, players):
        self.players = players # array of Players
        self.current_trick = None
        self.trick_history = [] # Trick class
        self.turn = None # Player
        self.dealer = None # Player
        self.phase = Phase.BID  # or "playing" or "scoring"


    def update_trick(self, trick):
        self.trick_history.append(self.current_trick)
        self.current_trick = trick

    def update_turn(self, player):
        self.turn = player

    def update_dealer(self, dealer):
        self.dealer = dealer

    def update_phase(self, phase):
        self.phase = phase

    def to_move(self):
        return self.turn
        


class Game():
    def __init__(self, players, team_mode=False):
        self.players = players
        self.teams = [Team(players[0], players[2]), Team(players[1], players[3])]
        self.discard = []
        self.trick = None
        self.turns_remaining = 13
        self.team_mode = team_mode
        self.game_state = GameState(players)

    def play_card(self):
        pass

    def build_deck(self):

        deck = []
        for s in range(4):
            for v in range(13):
                card = Card(s,v)
                if card not in deck:
                    deck.append(card)
        return deck
    
    def deal_hand(self):

        deck = self.build_deck()
        random.shuffle(deck)
        for p in self.players:
            for _ in range(13):
                card = deck.pop()
                p.hand.append(card)
    
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
        else:
            for p in self.players:
                print(p.score,"(",p.bags,")")

    def utility(self, state, players):
        return 1

    def actions(self, state):
        """Return a collection of the allowable moves from this state."""
        os = state.current_trick.opening_suit
        sb = state.current_trick.spades_broken
        valid_hand = []
        for card in state.turn.hand:
            # Returns hand of cards that match first played suit (or all but spades if first turn)
            if (card.suit == os or (os is None and card.suit != 0) or (os is None and sb)):
                valid_hand.append(card)
        if len(valid_hand) == 0: # Returns total hand if player can't match played suit
            valid_hand = deepcopy(state.turn.hand)
        valid_hand.sort(key=sortFunc)
        return valid_hand

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        state.current_trick.cards[state.turn.index] = move
        print(f"Player --------------------- {state.turn.index}")
        move.print()
        state.turn.print_hand()
        state.turn.hand.remove(move)


        if None not in state.current_trick.cards: # Checks if trick has been completed
            next_player_index = state.current_trick.evaluate_trick()
            state.update_turn(state.players[next_player_index])
            state.turn.tricks += 1
            state.trick_history.append(state.current_trick)
            state.current_trick.cards = [None for _ in range(4)]
            #self.assign_score_and_bags()
        else:
            next_player_index = state.turn.index + 1 if state.turn.index < 3 else 0
            state.update_turn(state.players[next_player_index])

        return state

    def is_terminal(self, state):
        if len(state.turn.hand) == 1:
            return True
        for player in state.players:
            if len(player.hand) > 0:
                return False
        return True


class MainGame(Game):
    def __init__(self, players, team_mode = False):
        super().__init__(players, team_mode)

    def play_card(self, p_index):
        current_p = self.players[p_index]
        if isinstance(current_p, MINMAXPlayer):
            played_card = current_p.make_move(self, self.game_state)
        else:
            played_card = current_p.make_move(self.trick)
        
        # self.game_state.players[p_index].print_hand()
        # played_card.print()
        # self.game_state.players[p_index].hand.remove(played_card)
        self.discard.append(played_card)

        print(f"Player {p_index+1} -> {val_dict[played_card.val]}-{suit_dict[played_card.suit]}")
        if self.trick.opening_suit is None: # Sets played_suit to suit of first played card
            self.trick.opening_suit = played_card.suit 
        if played_card == 0: # Allows spades to played as the opening card if one has been put down
            self.trick.spades_broken = True
        self.trick.cards[p_index] = played_card # Places card into the trick pile


    def play_round(self, starting_player):
        self.trick = Trick()
        self.game_state.update_trick(self.trick)
        p_index = self.players.index(starting_player)

        # Plays turn for each of the four players
        for i in range(4):
            self.game_state.update_turn(self.game_state.players[p_index])
            self.play_card(p_index)
            p_index = (p_index+1) if (p_index+1) < len(self.players) else 0 # Updates player index 
        winner_index = self.trick.evaluate_trick()
        self.players[winner_index].tricks += 1
        print(f"Player {winner_index+1} wins the trick! ({val_dict[self.trick.cards[winner_index].val]}-{suit_dict[self.trick.cards[winner_index].suit]})")
        print("-----------")
        self.turns_remaining -= 1
        if self.turns_remaining != 0: # Starts a new round if layers still have cards in their hand
            self.play_round(self.players[winner_index]) # Winning player begins the new trick
        else:
            self.assign_score_and_bags() # Tallys points at the end of a round
            self.print_scores()
            is_winner = self.check_for_winner(self.teams) if self.team_mode else self.check_for_winner(self.players)
            self.declare_winner() if is_winner else self.start_new_set()


    def declare_winner(self):

        highest_score = 0
        winning_index = 0
        if self.team_mode:
            for index, team in enumerate(self.teams):
                if team.score > highest_score:
                    winning_index = index
            print(f"Team {winning_index+1} wins!")
        else:
            for index, player in enumerate(self.players):
                if player.score > highest_score:
                    winning_index = index
            print(f"Player {winning_index+1} wins!")

    def start_new_set(self):
        '''
        Creates card deck, deals cards and has players make bets before starting a new round
        '''
        self.deal_hand()
        for i in range(2):
            self.teams[i].tricks = 0
            self.teams[i].bet = 0
        for i in range(4):
            self.players[i].hand.sort(key=sortFunc) # Sorts player hand
            self.players[i].tricks = 0
            self.players[i].make_bet()
            print(f"Player {i} Bet = {self.players[i].bet}")
        self.turns_remaining = 13
        self.play_round(self.players[0])
    
    def initialize_game(self):
        '''
        Initializes player and team properties for a new game
        '''
        for player in self.players:
            player.score = player.bags = player.bet = player.tricks = 0
        for team in self.teams:
            team.score = team.bags = team.bet = team.tricks = 0
        self.start_new_set()
 

infinity = math.inf

def minimax_search(game, state):

    def max_value(state):
        if game.is_terminal(state):
            return game.utility(state, state.to_move()), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a))
            if v2 > v:
                v, move = v2, a
        return v, move

    def min_value(state):
        if game.is_terminal(state):
            return game.utility(state, state.to_move()), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a))
            if v2 < v:
                v, move = v2, a
        return v, move

    return max_value(state)

p1 = AIPlayer(0)
p2 = AIPlayer(1)
p3 = AIPlayer(2)
p4 = MINMAXPlayer(3)  
g = MainGame([p1,p2,p3,p4], True)      
g.initialize_game()
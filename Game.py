import random
from copy import deepcopy

from Card import Card, Trick
from ISMCTS import ISMCTSPlayer

from Minimax.All import MINMAXAlphaBetaPlayer, GameState

import time

class Game():
    def __init__(self, players):
        self.players = players
        self.curr_player_index = 0
        self.teams = [Team(players[0], players[2]), Team(players[1], players[3])]
        self.discard = []
        self.trick = None
        self.turns_remaining = 13

    def sortSuitAndVal(self, e):
        return e.suit, e.val

    def get_next_player(self):
        '''
        Sets the current player turn to the next player in the game order
        '''
        self.curr_player_index = self.curr_player_index + 1 if self.curr_player_index < 3 else 0

    def play_card(self):
        pass

    def build_deck(self):
        '''
        Builds a deck of 52 unique cards

        Returns
        deck Card[]: array containing the deck of Cards
        '''
        deck = []
        for s in range(4):
            for v in range(13):
                card = Card(s,v)
                if card not in deck:
                    deck.append(card)
        return deck
    
    def deal_hand(self):
        '''
        Deals 13 cards to each player, removing them from the deck
        '''
        deck = self.build_deck()
        random.shuffle(deck)
        for p in self.players:
            for _ in range(13):
                card = deck.pop()
                p.hand.append(card)
    
    def get_player_score_and_bags(self, bet, tricks):
        '''
        Tallies a player's score and bags based on their bet and number of tricks

        Parameters:
        bet int: Number of bets made by a given player
        tricks int: Number of tricks made by a given player

        Returns
        score int: Player's score determined by their round performance
        bags int: Player's bags determined by how much they overbet
        '''
        if bet == 0:
            score, bags = self.check_nil_bet(tricks)
        else:
            score, bags = self.get_round_score(bet, tricks)
        return score, bags
    
    def get_round_score(self, bet, tricks):
        '''
        Gives or deducts points from a given player based on their bet and tricks

        Parameters:
        bet int: Number a given player bet at the start of a round
        tricks int: Number of tricks won by a given player

        Returns:
        score int: Updated score of the given player (+- bet*10 depending on if they met their bet)
        bags int: Updated number of bags a player has tallied
        '''
        score = -bet*10 if tricks < bet else bet*10
        bags = tricks-bet if tricks > bet else 0 # Adds bags to player total if bet was exceeded
        return score, bags
    
    def check_nil_bet(self, tricks):
        '''
        Handles case of a player making a nil bet

        Parameters:
        trick_count int: Number of tricks made by a given player

        Returns:
        score int: Updated score of the given player (+- 100 depending on if they met their bet)
        bags int: Updated number of bags a player has tallied
        '''
        if tricks == 0:
            score = 100
            bags = 0
        else:
            score = -100
            bags = tricks
        return score, bags

    def assign_score_and_bags(self):
        '''
        Tallies score and bags for all players/teams, starts new round if win condition not met by anyone
        '''
        for team in self.teams:
            for player in team.members: # Adds each team members score and bag sum to the team score and bag count
                if player.bet == 0: # Special case for nil betting
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
    
    def check_for_winner(self, player_array, threshold = 250):
        '''
        Checks if a player/team has exceed 500 points

        player_array []: Array of either Player or Team depending on game mode

        Returns:
        is_winner bool: True if at least one PLayer/Team exceeds 500 points
        '''
        is_winner = False
        for p in player_array:
            if p.score >= threshold or p.score <= -threshold:
                is_winner = True
                break
        return is_winner
        
    def print_scores(self):
        for t in self.teams:
            print(t.score,"(",t.bags,")")
     


class SimGame(Game):
    def __init__(self, players, curr_player_index, ai_player_index = None):
        super().__init__(players)
        self.curr_player_index = curr_player_index
        self.ai_player_index = ai_player_index if ai_player_index is not None else curr_player_index # Keeps reference of player that initiates the simulation
        self.ai_team_index = 0 if self.ai_player_index == 0 or self.ai_player_index == 2 else 1

    def play_card(self, card):
        '''
        Plays a card within a simulated version of the game

        Parameters:
        card Card: card object to be played
        '''
        self.trick.cards[self.curr_player_index] = card
        self.players[self.curr_player_index].hand.remove(card)
        if None not in self.trick.cards: # Checks if trick has been completed
            winning_index = self.trick.evaluate_trick()
            self.players[self.curr_player_index].tricks += 1
            self.curr_player_index = winning_index
            self.turns_remaining -= 1
            self.trick.cards = [None for _ in range(4)]
            if self.turns_remaining == 0:
                self.assign_score_and_bags()
        else:
            self.get_next_player()

    def clone_game(self):
        '''
        Creates a clone of the current game state to be used for simulation

        Returns:
        clone SimGame: a deepcopy of the current game state
        '''
        clone = SimGame(deepcopy(self.players), deepcopy(self.curr_player_index), deepcopy(self.ai_player_index))
        clone.trick = deepcopy(self.trick)
        clone.turns_remaining = deepcopy(self.turns_remaining)
        return clone
    
    def get_player_valid_cards(self):
        '''
        Gets the playable cards of the current active player in the current game state

        Returns:
        Card[]: array of playable cards
        '''
        player = self.players[self.curr_player_index]
        return player.get_valid_cards(self.trick.opening_suit, self.trick.spades_broken)
    

class MainGame(Game):
    def __init__(self, players):
        super().__init__(players)
        self.suit_dict = {0: '♠', 1: '♣', 2: '♥', 3: '♦'}
        self.val_dict = {0: '2', 1: '3', 2: '4', 3: '5',
                        4: '6', 5: '7', 6: '8', 7: '9',
                        8: '10', 9: 'J', 10: 'Q', 11: 'K',
                        12: 'A'}

    def play_card(self, p_index):
        '''
        Plays the current players turn and adds their card to the trick

        Parameters:
        p_index int: index of the current player in self.players
        '''
        current_p = self.players[p_index]
        if isinstance(current_p, ISMCTSPlayer): # Handles case for MCTS AI
            played_card = current_p.make_move(self.clone_game(p_index))
        elif isinstance(current_p, MINMAXAlphaBetaPlayer):
            played_card = current_p.make_move(self.clone_game(p_index), GameState(current_p))
        else:
            played_card = current_p.make_move(self.trick)
        self.discard.append(played_card)
        print(f"Player {p_index+1} -> {self.val_dict[played_card.val]}-{self.suit_dict[played_card.suit]}")
        if self.trick.opening_suit is None: # Sets played_suit to suit of first played card
            self.trick.opening_suit = played_card.suit 
        if played_card == 0: # Allows spades to played as the opening card if one has been put down
            self.trick.spades_broken = True
        self.trick.cards[p_index] = played_card # Places card into the trick pile


    def play_round(self, starting_player_index):
        '''
        Plays a hand of Spades, giving each player a turn to play a card

        Parameters:
        starting_player Player: Indicates which player plays the first card
        '''
        self.trick = Trick()
        self.curr_player_index = starting_player_index

        # Plays turn for each of the four players
        for _ in range(4):
            self.play_card(self.curr_player_index)
            self.get_next_player()
        winner_index = self.trick.evaluate_trick()
        self.players[winner_index].tricks += 1
        print(f"Player {winner_index+1} wins the trick! ({self.val_dict[self.trick.cards[winner_index].val]}-{self.suit_dict[self.trick.cards[winner_index].suit]})")
        print("-----------")
        self.turns_remaining -= 1
        if self.turns_remaining != 0: # Starts a new round if layers still have cards in their hand
            self.play_round(winner_index) # Winning player begins the new trick
        else:
            self.assign_score_and_bags() # Tallys points at the end of a round
            self.print_scores()
            is_winner = self.check_for_winner(self.teams) if self.team_mode else self.check_for_winner(self.players)
            self.declare_winner() if is_winner else self.start_new_set()


    def declare_winner(self):
        '''
        Checks for team/player with highest score in case where more than one breaks 500 points
        '''
        highest_score = 0
        winning_index = 0
        for index, team in enumerate(self.teams):
            if team.score > highest_score:
                winning_index = index
                highest_score = team.score
        print(f"Team {winning_index+1} wins!")

    def start_new_set(self):
        '''
        Creates card deck, deals cards and has players make bets before starting a new round
        '''
        self.deal_hand()
        for i in range(2):
            self.teams[i].tricks = 0
            self.teams[i].bet = 0
        for i in range(4):
            self.players[i].hand.sort(key=self.sortSuitAndVal) # Sorts player hand
            self.players[i].tricks = 0
            self.players[i].make_bet()
            print(f"Player {i+1} Bet = {self.players[i].bet}")
        self.turns_remaining = 13
        start = time.time()
        self.play_round(self.curr_player_index)
        end = time.time()
        duration = end - start
        print (f'Round Time: {duration}')
    
    def initialize_game(self):
        '''
        Initializes player and team properties for a new game
        '''
        for player in self.players:
            player.score = player.bags = player.bet = player.tricks = 0
        for team in self.teams:
            team.score = team.bags = team.bet = team.tricks = 0
        self.start_new_set()
    
    def clone_game(self, player_index):
        '''
        Clones the game state data for ICMCTS

        Parameters:
        player_index int: IDs player who's turn is currently active

        Returns:
        clone SimGame: Captures the current game state data
        '''
        clone = SimGame(deepcopy(self.players), player_index)
        clone.discard= deepcopy(self.discard)
        clone.trick = deepcopy(self.trick)
        clone.turns_remaining= deepcopy(self.turns_remaining)
        return clone
    
class Team:
    def __init__(self, p1, p2):
        self.members = [p1, p2]
        self.tricks = 0
        self.bet = 0
        self.bags = 0
        self.score = 0
        
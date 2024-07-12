import random
import numpy as np
from copy import deepcopy


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

class Trick:
    def __init__(self):
        self.cards = [None for i in range(4)]
        self.opening_suit = None
        self.spades_broken = False
    
    def evaluate_trick(self):
        '''
        Determines which card in a given trick has the highest value

        Returns:
        winning_index int: The index of the winning player in the Game.players array
        '''
        highest_val = 0
        winning_index = 0
        for index, card in enumerate(self.cards):
            if card.suit == 0 and self.opening_suit != 0:
                self.opening_suit = 0
                highest_val = card.val
                winning_index = index
            elif card.suit == self.opening_suit and card.val >= highest_val: # Checks if same suit card is the highest value
                highest_val = card.val
                winning_index = index
        return winning_index
    
class Team:
    def __init__(self, p1, p2):
        self.members = [p1, p2]
        self.bags = 0
        self.score = 0
	        
class Player:

    def __init__(self):
        self.hand = []
        self.legal_moves = []
        self.bet = 0
        self.tricks = 0
        self.bags = 0
        self.score = 0

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
    
    def make_bet(self):
        nil_bet = False
        expected_tricks = self.evaluate_regular_bet()
        if expected_tricks <= 2 and Card(0, 12) not in self.hand:
            nil_bet = self.evaluate_nil_bet()
        self.bet = 0 if nil_bet else expected_tricks


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
            print(f"{val_dict[card.val]}-{suit_dict[card.suit]}" , end = " ")
        print("]")

    
    def get_valid_cards(self, opening_suit, spades_broken):
        '''
        Returns the array of eligible cards (moves) a player has

        Parameters:
        hand Card[]: a list of cards held by some player

        Returns:
        valid_hand Card[]: a pruned version of hand containing only the cards that can currently be played
        '''
        valid_hand = []
        for card in self.hand:
            # Returns hand of cards that match first played suit (or all but spades if first turn)
            if (card.suit == opening_suit or (opening_suit is None and card.suit != 0) or (opening_suit is None and spades_broken)):
                valid_hand.append(card)
        if len(valid_hand) == 0: # Returns total hand if player can't match played suit
            valid_hand = deepcopy(self.hand)
        valid_hand.sort(key=sortFunc)
        return valid_hand
    
class HumanPlayer(Player):

    def __init__(self):
        super().__init__()

    def make_bet(self):
        self.tricks = 0 # Resets trick count before each new round
        for card in self.hand:
            print(f"{val_dict[card.val]}-{suit_dict[card.suit]}" , end = " ")
        print("")
        bet = int(input("Bet how many tricks you expect to win:"))
        while not isinstance(bet, int) or bet < 0 or bet > 13:
            bet = int(input("Please make a bet between 0 and 13"))
        self.bet = bet
	
    def make_move(self, trick):
        '''
        Takes user input to decide on a move

        Parameters:
        trick Trick: used for deriving valid_cards

        Returns:
        selected_card Card: Chosen card to play
        '''
        print("Player Move!")
        valid_hand = self.get_valid_cards(trick.opening_suit, trick.spades_broken) # Gets array of eligible cards to play
        for index, card in enumerate(valid_hand):
            print(f"{index}. {val_dict[card.val]}-{suit_dict[card.suit]}" , end = " ")
        print("")
        selected_index = int(input("Select a card to play:"))
        while not isinstance(selected_index, int) or selected_index < 0 or selected_index >= len(valid_hand):
            selected_index = int(input("Choose a valid card:"))
        selected_card = valid_hand[selected_index]
        self.hand.remove(selected_card)
        return selected_card
    
    
class AIPlayer(Player):
    def __init__(self):
        super().__init__()

    def make_bet(self):
        self.bet = random.randint(2,5)

    def make_move(self, trick):
        valid_hand = self.get_valid_cards(trick.opening_suit, trick.spades_broken)
        selected_card = random.choice(valid_hand)
        self.hand.remove(selected_card)
        return selected_card


class ISMCTSPlayer(Player):
    def __init__(self):
        super().__init__()

    def make_move(self, game, iterations = 1500):
        '''
        Chooses card to play using ISMCTS

        Parameters:
        game SimGame:copy of the game state up to the MCTS player's intiial turn
        iterations int: number of iterations to run MCTS

        Returns:
        move Card: card to be played in the actual game
        '''
        root = MCTSNode()
        self.print_hand()
        for _ in range(iterations):
            #print("I = "+str(i))
            node = root
            clone_game = self.determinize(game.clone_game()) # Randomizes non-player hands
            self.MCTS(clone_game, node)
        max_visits = 0
        move = None
        for child in root.children:
            if child.visits > max_visits:
                max_visits = child.visits
                move = child.last_card
        self.hand.remove(move)
        return move

    def determinize(self, game):
        '''
        Randomizes the hands of each non-MCTS player

        Parameters:
        game SimGame: copy of the game state up to the MCTS player's intiial turn

        Returns:
        game SimGame: copy of game state with randomized hands
        '''
        unseen_cards = []
        hand_sizes = [0 for _ in range(4)] # Saves how many cards each player has before randomizing
        for index, p in enumerate(game.players): # Collects all of the unseen cards
            if p != game.players[game.player_index]:
                hand_sizes[index] = len(p.hand)
                for c in p.hand:
                    unseen_cards.append(c)
                p.hand = []
        random.shuffle(unseen_cards)
        for index, p in enumerate(game.players): # Inserts randomized cards back into non-player hands
            if p != self:
                #print(f"Player {index} => [ ", end = "")
                for _ in range(hand_sizes[index]):
                    game.players[index].hand.append(unseen_cards[0])
                    #print(f"{val_dict[unseen_cards[0].val]}{suit_dict[unseen_cards[0].suit]}", end = " ")
                    unseen_cards.pop(0)
                    
        return game

    def MCTS(self, game, node):
        '''
        Implementation of the ISMCTS algorithm, simulates a round and updates node stats

        Parameters:
        game SimGame: copy of the game state up to the MCTS player's intiial turn
        node Node: root of the search tree beginning the the MCTS player's initial turn
        '''

        # Select child nodes up to a leaf
        while len(node.children) > 0 and node.is_fully_expanded(game.get_player_valid_cards()):
            node = node.UCT(game.get_player_valid_cards())
            game.play_card(node.last_card)

        # Expand non-terminal leaf node
        player = game.players[game.player_index]
        child_cards = [child.last_card for child in node.children]
        valid_cards =  game.get_player_valid_cards()
        valid_cards[:] = [card for card in valid_cards if card not in child_cards]
        if len(valid_cards) > 0:
            random_card = random.choice(valid_cards)
            child = MCTSNode(node, random_card, player)
            node.children.append(child)
            node = child
            game.play_card(random_card)

        # Simulate remainder of round
        while (game.turns_remaining) > 0:
            valid_cards = game.get_player_valid_cards()
            game.play_card(random.choice(valid_cards))
            
        # Backpropigate to root
        while node is not None:
            node.update_node(game)
            node = node.parent


class MCTSNode:

    def __init__(self, parent = None, last_card = None, last_player = None):
        self.parent = parent
        self.last_card = last_card
        self.last_player = last_player
        self.children = []
        self.visits = 0
        self.score_sum = 0
        self.expected_score = 0

    def add_child(self, card, player):
        '''
        Adds a child node to the search tree

        Parameters:
        card Card: Adds the last played card to the newly created Node
        player int: Adds index of player who played card to node
        '''
        child = MCTSNode(self, card, player)
        self.children.append(child)

    def is_fully_expanded(self, valid_cards):
        '''
        Checks in the select phase if all possible moves have been explored

        Parameters:
        valid_cards Card[]: List of cards availible to use in current determinization of the game
        
        fully_expanded bool: Returns True/False depending on if all possible cards have been explored
        '''
        fully_expanded = False
        child_cards = [child.last_card for child in self.children]
        if all(card in child_cards for card in valid_cards):
            fully_expanded = True
        return fully_expanded

    
    def update_node(self, game, constant = 0.7):
        '''
        Updates travseral statistics of node

        Parameters:
        game SimGame: A copy of the current game state
        constant float: used for deriving the statistic
        '''
        self.visits += 1
        if game.team_mode:
            opp_index = abs(1-self.ai_player_index) # Gets index for opposing team
            ai_team = game.teams[game.ai_team_index]
            opp_team = game.teams[opp_index]
            self.score_sum += ((ai_team.score-5*ai_team.bags)-(opp_team.score-5*opp_team.bags)/constant)
            self.expected_score = ((ai_team.score-10*ai_team.bags)-(opp_team.score-10*opp_team.bags)/0.7)
        else:
            highest_score = highest_score_index = 0
            ai_player = game.players[game.ai_player_index]
            for index, player in enumerate(game.players):
                if player != ai_player:
                    if player.score > highest_score:
                        highest_score = player.score
                        highest_score_index = index
            opp_player = game.players[highest_score_index]
            self.score_sum += ((ai_player.score-5*ai_player.bags)-(opp_player.score-5*opp_player.bags)/constant)
            self.expected_score = ((ai_player.score-10*ai_player.bags)-(opp_player.score-10*opp_player.bags)/constant)
        #self.expected_score = self.score_sum/self.visits # Takes the average of all score outcomes


    def UCT(self, valid_cards, constant = 0.7):
        '''
        Selection policy for chosing a node in the tree

        Parameters:
        valid_cards Card[]: List of cards availible to use in current determinization of the game
        constant float: used for deriving the statistic

        Returns:
        selected_child Node: Node with the highest selection policy value
        '''
        explorable_children = []
        child_cards = [child.last_card for child in self.children]
        for index, card in enumerate(child_cards):
            if card in valid_cards:
                explorable_children.append(self.children[index])
        max_conf = float('-inf')
        selected_child = None
        for c in explorable_children: # Selects a node to traverse using UCT selection policy
            child_conf = c.expected_score + constant*np.sqrt(np.log(self.visits))/float(c.visits)
            if child_conf > max_conf:
                max_conf = child_conf
                selected_child = c
        return selected_child

    

class Game():
    def __init__(self, players, team_mode=False):
        self.players = players
        self.teams = [Team(players[0], players[2]), Team(players[1], players[3])]
        self.discard = []
        self.trick = None
        self.turns_remaining = 13
        self.team_mode = team_mode

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
        '''
        Checks if a player/team has exceed 500 points

        player_array []: Array of either Player or Team depending on game mode

        Returns:
        is_winner bool: True if at least one PLayer/Team exceeds 500 points
        '''
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


class SimGame(Game):
    def __init__(self, players, player_index, ai_player_index = None, team_mode=False):
        super().__init__(players, team_mode)
        self.player_index = player_index
        self.ai_player_index = ai_player_index if ai_player_index is not None else player_index # Keeps reference of player that initiates the simulation
        self.ai_team_index = 0 if self.ai_player_index == 0 or self.ai_player_index == 2 else 1

    def play_card(self, card):
        self.trick.cards[self.player_index] = card
        self.players[self.player_index].hand.remove(card)
        if None not in self.trick.cards: # Checks if trick has been completed
            winning_index = self.trick.evaluate_trick()
            self.players[self.player_index].tricks += 1
            self.player_index = winning_index
            self.turns_remaining -= 1
            self.trick.cards = [None for _ in range(4)]
            if self.turns_remaining == 0:
                self.assign_score_and_bags()
        else:
            self.player_index = self.player_index + 1 if self.player_index < 3 else 0

    def clone_game(self):
        '''
        Creates a clone of the current game state to be used for simulation

        Returns:
        clone SimGame: a deepcopy of the current game state
        '''
        clone = SimGame(deepcopy(self.players), deepcopy(self.player_index), deepcopy(self.ai_player_index))
        clone.trick = deepcopy(self.trick)
        clone.turns_remaining = deepcopy(self.turns_remaining)
        return clone
    
    def get_player_valid_cards(self):
        '''
        Gets the playable cards of the current active player in the current game state

        Returns:
        Card[]: array of playable cards
        '''
        player = self.players[self.player_index]
        return player.get_valid_cards(self.trick.opening_suit, self.trick.spades_broken)
    

class MainGame(Game):
    def __init__(self, players, team_mode = False):
        super().__init__(players, team_mode)

    def play_card(self, p_index):
        '''
        Plays the current players turn and adds their card to the trick

        Parameters:
        p_index int: index of the current player in self.players
        '''
        current_p = self.players[p_index]
        if isinstance(current_p, ISMCTSPlayer): # Handles case for MCTS AI
            played_card = current_p.make_move(self.clone_game(p_index))
        else:
            played_card = current_p.make_move(self.trick)
        self.discard.append(played_card)
        print(f"Player {p_index+1} -> {val_dict[played_card.val]}-{suit_dict[played_card.suit]}")
        if self.trick.opening_suit is None: # Sets played_suit to suit of first played card
            self.trick.opening_suit = played_card.suit 
        if played_card == 0: # Allows spades to played as the opening card if one has been put down
            self.trick.spades_broken = True
        self.trick.cards[p_index] = played_card # Places card into the trick pile


    def play_round(self, starting_player):
        '''
        Plays a hand of Spades, giving each player a turn to play a card

        Parameters:
        starting_player Player: Indicates which player plays the first card
        '''
        self.trick = Trick()
        p_index = self.players.index(starting_player)

        # Plays turn for each of the four players
        for i in range(4):
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
        '''
        Checks for team/player with highest score in case where more than one breaks 500 points
        '''
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
            

p1 = AIPlayer()
p2 = ISMCTSPlayer()
p3 = AIPlayer()
p4 = ISMCTSPlayer()  
g = MainGame([p1,p2,p3,p4], True)      
g.initialize_game()

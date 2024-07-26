import random
from copy import deepcopy

from Card import Card, Trick
from ISMCTS import ISMCTSPlayer

# class Card:
#     def __init__(self,suit,val):
#         self.suit = suit
#         self.val = val

#     def __eq__(self, other):
#         if not isinstance(other, Card):
#             return NotImplemented
#         return self.suit == other.suit and self.val == other.val

# class Trick:
#     def __init__(self):
#         self.cards = [None for _ in range(4)]
#         self.opening_suit = None
#         self.spades_broken = False
    
#     def evaluate_trick(self):
#         '''
#         Determines which card in a given trick has the highest value

#         Returns:
#         winning_index int: The index of the winning player in the Game.players array
#         '''
#         highest_val = 0
#         winning_index = 0
#         for index, card in enumerate(self.cards):
#             if card.suit == 0 and self.opening_suit != 0:
#                 self.opening_suit = 0
#                 highest_val = card.val
#                 winning_index = index
#             elif card.suit == self.opening_suit and card.val >= highest_val: # Checks if same suit card is the highest value
#                 highest_val = card.val
#                 winning_index = index
#         return winning_index
    

	        
# class Player:

#     def __init__(self):
#         self.hand = []
#         self.legal_moves = []
#         self.bet = 0
#         self.tricks = 0
#         self.bags = 0
#         self.score = 0

#         # Probability table for non-spades suits developed by Cohensius et al.
#         self.probability_table = {
#             0: {0: 0.997, 1: 0.966, 2: 0.817},
#             1: {0: 0.994, 1: 0.942, 2: 0.733},
#             2: {0: 0.990, 1: 0.907, 2: 0.624},
#             3: {0: 0.983, 1: 0.855, 2: 0.489},
#             4: {0: 0.970, 1: 0.779, 2: 0.350},
#             5: {0: 0.948, 1: 0.678, 2: 0.212},
#             6: {0: 0.915, 1: 0.544, 2: 0.095},
#             7: {0: 0.857, 1: 0.381, 2: 0.025},
#             8: {0: 0.774, 1: 0.214, 2: 0},
#             9: {0: 0.646, 1: 0.074, 2: 0},
#             10: {0: 0.462, 1: 0, 2: 0},
#             11: {0: 0.227, 1: 0, 2: 0},
#             12: {0: 0, 1: 0, 2: 0}
#         }

#     def sortSuitAndVal(e):
#         return e.suit, e.val

#     def __eq__(self, other):
#         if not isinstance(other, Player):
#             return NotImplemented
#         return self.hand == other.hand
    
#     def make_bet(self):
#         '''
#         Evaluates hand and given PT to make a viable bet
#         '''
#         nil_bet = False
#         expected_tricks = self.evaluate_regular_bet()
#         if expected_tricks == 1 and Card(0, 12) not in self.hand:
#             nil_bet = self.evaluate_nil_bet()
#         self.bet = 0 if nil_bet else expected_tricks


#     def evaluate_regular_bet(self):
#         '''
#         Iterates through the different suits to determine the expected trick take

#         Returns:
#         round(expected_tricks) int: The number of tricks expected to be taken with current hand
#         '''
#         expected_tricks = 0
#         for i in range(4):
#             suit_arr = [card for card in self.hand if card.suit == i]
#             suit_arr.reverse()
#             suit_count = len(suit_arr)
#             if i == 0: # Case for evaluating Spades
#                 high_value_spades = [card for card in suit_arr if card.val >= 9] # Only concerned with spades of val J-A
#                 for index, card in enumerate(high_value_spades):
#                     higher_value_cards = abs(12 - card.val)
#                     # The J-Q-K-A spades are each worth a trick if there are more spades in hand than number of un-owned higher-ranked spades
#                     if (suit_count > higher_value_cards-index): # Subtract number of higher owned cards
#                         expected_tricks+=1
#                 if suit_count >= 5: # Add a trick for every spade in hand over the fourth
#                     expected_tricks += suit_count - 4
#             else: # Case for non-Spade suits
#                 probabilities = self.probability_table[suit_count]
#                 for card in suit_arr:
#                     if card.val == 12:
#                         expected_tricks += probabilities[0]
#                     elif card.val == 11:
#                         expected_tricks += probabilities[1]
#                     elif card.val == 10: 
#                         expected_tricks += probabilities[2]
#                     else:
#                         break
#         return round(expected_tricks) if round(expected_tricks) > 0 else 1

#     def evaluate_nil_bet(self):
#         '''
#         Checks if a nil bet is a viable choice

#         Returns:
#         bool: True if a nil bet is deemed to be a low risk option
#         '''
#         for i in range(4):
#             suit_arr = [card for card in self.hand if card.suit == i]
#             if len(suit_arr) > 0:
#                 suit_arr.reverse()
#                 if i == 0 and suit_arr[0].val > 8: # Ensures we don't nil bet with a face value spade
#                     return False
#                 last_three = suit_arr[-3:] # Gets the three lowest value cards for the given suit
#                 if len(last_three) > 0 and last_three[0].val > 8: # Checks if the suit hand is 'unsafe' (Bottom 3 value cards contain J or greater)
#                     return False
#         # print('ATTEMPTING NIL')
#         return True
    
    
#     def make_move(self):
#         pass
    
#     def print_hand(self):
#         print("[", end=" ")
#         for card in self.hand:
#             print(f"{val_dict[card.val]}-{suit_dict[card.suit]}" , end = " ")
#         print("]")

    
#     def get_valid_cards(self, opening_suit, spades_broken):
#         '''
#         Returns the array of eligible cards (moves) a player has

#         Parameters:
#         hand Card[]: a list of cards held by some player

#         Returns:
#         valid_hand Card[]: a pruned version of hand containing only the cards that can currently be played
#         '''
#         valid_hand = []
#         for card in self.hand:
#             # Returns hand of cards that match first played suit (or all but spades if first turn)
#             if (card.suit == opening_suit or (opening_suit is None and card.suit != 0) or (opening_suit is None and spades_broken)):
#                 valid_hand.append(card)
#         if len(valid_hand) == 0: # Returns total hand if player can't match played suit
#             valid_hand = deepcopy(self.hand)
#         valid_hand.sort(key=sortSuitAndVal)
#         return valid_hand
    
# class HumanPlayer(Player):

#     def __init__(self):
#         super().__init__()

#     def make_bet(self):
#         self.tricks = 0 # Resets trick count before each new round
#         for card in self.hand:
#             print(f"{val_dict[card.val]}-{suit_dict[card.suit]}" , end = " ")
#         print("")
#         bet = int(input("Bet how many tricks you expect to win:"))
#         while not isinstance(bet, int) or bet < 0 or bet > 13:
#             bet = int(input("Please make a bet between 0 and 13"))
#         self.bet = bet
	
#     def make_move(self, trick):
#         '''
#         Takes user input to decide on a move

#         Parameters:
#         trick Trick: used for deriving valid_cards

#         Returns:
#         selected_card Card: Chosen card to play
#         '''
#         print("Player Move!")
#         valid_hand = self.get_valid_cards(trick.opening_suit, trick.spades_broken) # Gets array of eligible cards to play
#         for index, card in enumerate(valid_hand):
#             print(f"{index}. {val_dict[card.val]}-{suit_dict[card.suit]}" , end = " ")
#         print("")
#         selected_index = int(input("Select a card to play:"))
#         while not isinstance(selected_index, int) or selected_index < 0 or selected_index >= len(valid_hand):
#             selected_index = int(input("Choose a valid card:"))
#         selected_card = valid_hand[selected_index]
#         self.hand.remove(selected_card)
#         return selected_card
    
    
# class RandomPlayer(Player):
#     def __init__(self):
#         super().__init__()

#     def make_move(self, trick):
#         valid_hand = self.get_valid_cards(trick.opening_suit, trick.spades_broken)
#         selected_card = random.choice(valid_hand)
#         self.hand.remove(selected_card)
#         return selected_card


# class ISMCTSPlayer(Player):
#     def __init__(self):
#         super().__init__()

#     def make_move(self, game, iterations = 500):
#         '''
#         Chooses card to play using ISMCTS

#         Parameters:
#         game SimGame:copy of the game state up to the MCTS player's intiial turn
#         iterations int: number of iterations to run MCTS

#         Returns:
#         move Card: card to be played in the actual game
#         '''
#         valid_hand = self.get_valid_cards(game.trick.opening_suit, game.trick.spades_broken)
#         if len(valid_hand) > 1: # Only runs MCTS if player has a choice of cards
#             root = MCTSNode()
#             #self.print_hand()
#             start = time.time()
#             unseen_cards = self.get_unseen_cards(game) # Cards that are yet to be played from other players
#             #iterations = iterations+(int(iterations/2)*(13-game.turns_remaining))
#             for _ in range(iterations):
#                 node = root
#                 clone_game = self.determinize(game.clone_game(), deepcopy(unseen_cards)) # Randomizes non-player hands
#                 self.MCTS(clone_game, node, min_visits = iterations/10)
#             max_visits = 0
#             move = None
#             for child in root.children:
#                 if child.visits > max_visits:
#                     max_visits = child.visits
#                     move = child.last_card
#             end = time.time()
#             duration = end-start
#             #print(f"Time to make decision: {duration} seconds")
#         else:
#             move = valid_hand[0]
#         self.hand.remove(move)
#         return move
    
#     def get_unseen_cards(self, game):
#         unseen_cards = []
#         for p in game.players: # Collects all of the unseen cards
#             if p != game.players[game.curr_player_index]:
#                 for c in p.hand:
#                     unseen_cards.append(c)
#         return unseen_cards

#     def determinize(self, game, unseen_cards):
#         '''
#         Randomizes the hands of each non-MCTS player

#         Parameters:
#         game SimGame: copy of the game state up to the MCTS player's intiial turn

#         Returns:
#         game SimGame: copy of game state with randomized hands
#         '''
#         random.shuffle(unseen_cards)
#         high_value_cards = [card for card in unseen_cards if card.suit == 0 and card.val >= 6 or card.val >= 10] # Gets card with high-trick taking potential
#         high_value_count = len(high_value_cards)
#         unseen_cards = [card for card in unseen_cards if card not in high_value_cards] # Removes duplicate cards from unseen_cards
#         total_bet_difference = 0
#         hand_sizes = [0 for _ in range(4)]
        
#         # Takes each player's hand size and an estiamte of how many high value cards they are likely to hold
#         for index, p in enumerate(game.players):
#             if p != game.players[game.curr_player_index]:
#                 hand_sizes[index] = len(p.hand)
#                 total_bet_difference += max(0,((p.bet-p.tricks)))
#                 p.hand = []

#         # Deal high value cards based on which players are most likely to have them
#         if (total_bet_difference > 0):
#             for index, p in enumerate(game.players):
#                 if p != game.players[game.curr_player_index]:
#                     player_bet_difference = max(0, p.bet-p.tricks)
#                     high_card_likelihood = player_bet_difference/total_bet_difference
#                     cards_to_draw = math.ceil(high_value_count*high_card_likelihood) if math.ceil(high_value_count*high_card_likelihood) < hand_sizes[index] else hand_sizes[index]
#                     for _ in range(cards_to_draw):
#                         if (len(high_value_cards) > 0):
#                             p.hand.append(high_value_cards[0])
#                             high_value_cards.pop(0)
        
#         if len(high_value_cards) > 0:
#             unseen_cards.extend(high_value_cards)
#             random.shuffle(unseen_cards)

#         # Deals the remainder of the deck
#         for index, p in enumerate(game.players): # Inserts randomized cards back into non-player hands
#             if p != game.players[game.curr_player_index]:
#                 hand_remainder = hand_sizes[index]-len(p.hand)
#                 for _ in range(hand_remainder):
#                     p.hand.append(unseen_cards[0])
#                     unseen_cards.pop(0) 
#         return game

#     def MCTS(self, game, node, min_visits):
#         '''
#         Implementation of the ISMCTS algorithm, simulates a round and updates node stats

#         Parameters:
#         game SimGame: copy of the game state up to the MCTS player's intiial turn
#         node Node: root of the search tree beginning the the MCTS player's initial turn
#         '''

#         # Select child nodes up to a leaf
#         while len(node.children) > 0:
#             valid_cards = game.get_player_valid_cards()
#             if node.is_fully_expanded(valid_cards):
#                 is_opponent = (game.players[game.curr_player_index] not in game.teams[game.ai_team_index].members) # Checks if player is on the AI's team
#                 node = node.UCT(valid_cards, min_visits, is_opponent)
#                 game.play_card(node.last_card)
#             else:
#                 break

#         # Expand non-terminal leaf node
#         child_cards = [child.last_card for child in node.children]
#         valid_cards =  game.get_player_valid_cards()
#         valid_cards[:] = [card for card in valid_cards if card not in child_cards]
#         if len(valid_cards) > 0:
#             #random_card = random.choice(valid_cards)
#             probable_card = self.guess_next_card(game, valid_cards)
#             child = MCTSNode(node, probable_card, game.players[game.curr_player_index])
#             # child.visits += child.last_card.val
#             node.children.append(child)
#             game.play_card(probable_card)
#             node = child

#         # Simulate remainder of round
#         while (game.turns_remaining) > 0:
#             valid_cards = game.get_player_valid_cards()
#             probable_card = self.guess_next_card(game, valid_cards)
#             game.play_card(probable_card)
            
#         # Backpropigate to root
#         while node is not None:
#             node.update_node(game)
#             node = node.parent
        

#     def guess_next_card(self, game, valid_cards):
#         '''
#         Evaluates a given players hand to logically assess their most likely next move

#         Parameters:
#         game SimGame: copy of the current game state
#         valid_cards Card[]: Array of Cards that a player can legally play

#         Returns:
#         Card: The most beneficial card a player can play based on a series of conditions
#         '''
#         trick_suit = game.trick.opening_suit
#         current_player = game.players[game.curr_player_index]
#         cards_in_trick = [card for card in game.trick.cards if card is not None]
#         suits_in_hand = [card for card in valid_cards if card.suit == trick_suit] # Cards in player hand that match trick suit
#         spades_in_trick = []
#         spades_in_hand = []
#         if trick_suit != 0:
#             spades_in_trick = [card for card in game.trick.cards if card is not None and card.suit == 0]
#             spades_in_hand = [card for card in valid_cards if card.suit == 0] # Cards in player hand that are spades
        
#         # Case if cards have been played in the trick
#         if len(cards_in_trick) > 0:

#             # Case for regular bets
#             if (current_player.bet != 0):

#                 # Checks if a playing a spade is possible
#                 if len(spades_in_hand) > 0 and trick_suit != 0:
#                     if len(spades_in_trick) > 0: # Checks if a spade has already been played
#                         highest_spade = max(spades_in_hand, key=lambda card: card.val)
#                         if highest_spade.val > max(spades_in_hand, key=lambda card: card.val).val: 
#                             return highest_spade
#                     return min(spades_in_hand, key=lambda card: card.val)
                
#                 # Checks if player has suits matching the trick
#                 elif len(suits_in_hand) > 0: 
#                     highest_card_of_trick = max(cards_in_trick, key=lambda card: card.val and card.suit == trick_suit and card is not None)
#                     max_of_suit = max(suits_in_hand, key=lambda card: card.val)
#                     min_of_suit = min(suits_in_hand, key=lambda card: card.val)
#                     if max_of_suit.val > highest_card_of_trick.val and len(spades_in_trick) == 0: # Checks if player can take the trick
#                         return max_of_suit
#                     else:
#                         return min_of_suit
                    
#                 # Checks if player has no spades or matching suits
#                 else: 
#                     valid_cards.sort(key=sortVal)
#                     return valid_cards[0] # Returns lowest value of another suit

#             # Case for nil bets
#             else:
#                 # Checks if a spade can be safely discarded
#                 if len(spades_in_trick) > 0 and len(spades_in_hand) > 0:
#                     highest_spade_of_trick = max(spades_in_trick, key=lambda card: card.val)
#                     highest_spade = max(spades_in_hand, key=lambda card: card.val)
#                     if highest_spade.val < highest_spade_of_trick.val:  # Checks if highest spade can be safely discarded
#                         return highest_spade
#                     spades_less_than_max = [spade for spade in spades_in_hand if spade.val < highest_spade_of_trick.val]
#                     if len(spades_less_than_max) > 0: # Plays the highest spade card that is guarenteed to not win trick
#                             return max(spades_less_than_max, key=lambda card: card.val)
                
#                 # Checks if a card of the same suit can be discarded
#                 if len(suits_in_hand) > 0:
#                     highest_card_of_trick = max(cards_in_trick, key=lambda card: card.val and card.suit == trick_suit and card is not None)
#                     max_of_suit = max(suits_in_hand, key=lambda card: card.val)
#                     if (max_of_suit.val < highest_card_of_trick.val) or len(spades_in_trick) > 0: # Plays highest card if its less than the leading trick card
#                         return max_of_suit
#                     else:
#                         suits_less_than_max = [suit for suit in suits_in_hand if suit.val < highest_card_of_trick.val]
#                         if len(suits_less_than_max) > 0: # Otherwise lays the highest card that is guarenteed to not win trick
#                             return max(suits_less_than_max, key=lambda card: card.val)
                
#                 # Returns highest value of another suit to be safely discarded
#                 valid_cards.sort(key=sortVal)
#                 return valid_cards[-1] 
        
#         # Case if player is first to play card
#         else:
#             valid_cards.sort(key=sortVal)
#             if (current_player.bet != 0): 
#                 return valid_cards[-1] # Plays highest value card in valid cards
#             else:
#                 return valid_cards[0] # Minimizes chance of winning trick with low val card


# class MCTSNode:

#     def __init__(self, parent = None, last_card = None, last_player = None):
#         self.parent = parent
#         self.last_card = last_card
#         self.last_player = last_player
#         self.children = []
#         self.visits = 0
#         self.score_sum = 0
#         self.expected_score = 0

#     def add_child(self, card, player):
#         '''
#         Adds a child node to the search tree

#         Parameters:
#         card Card: Adds the last played card to the newly created Node
#         player int: Adds index of player who played card to node
#         '''
#         child = MCTSNode(self, card, player)
#         self.children.append(child)

#     def is_fully_expanded(self, valid_cards):
#         '''
#         Checks in the select phase if all possible moves have been explored

#         Parameters:
#         valid_cards Card[]: List of cards availible to use in current determinization of the game
        
#         fully_expanded bool: Returns True/False depending on if all possible cards have been explored
#         '''
#         fully_expanded = False
#         child_cards = [child.last_card for child in self.children]
#         if all(card in child_cards for card in valid_cards):
#             fully_expanded = True
#         return fully_expanded

    
#     def update_node(self, game, constant = 500):
#         '''
#         Updates travseral statistics of node

#         Parameters:
#         game SimGame: A copy of the current game state
#         constant float: used for deriving the statistic
#         '''
#         self.visits += 1
#         if game.team_mode:
#             ai_team = game.teams[game.ai_team_index]
#             opp_team = game.teams[abs(1-game.ai_team_index)]
#             self.score_sum += ((ai_team.score-10*ai_team.bags)-(opp_team.score-10*opp_team.bags))/constant
#             #self.expected_score = ((ai_team.score-10*ai_team.bags)-(opp_team.score-10*opp_team.bags))/constant
#         else:
#             highest_score = highest_score_index = 0
#             ai_player = game.players[game.ai_player_index]
#             for index, player in enumerate(game.players):
#                 if player != ai_player:
#                     if player.score > highest_score:
#                         highest_score = player.score
#                         highest_score_index = index
#             opp_player = game.players[highest_score_index]
#             self.score_sum += ((ai_player.score-10*ai_player.bags)-(opp_player.score-10*opp_player.bags))/constant
#             #self.expected_score = ((ai_player.score-10*ai_player.bags)-(opp_player.score-10*opp_player.bags))/constant
#         self.expected_score = self.score_sum/self.visits # Takes the average of all score outcomes


#     def UCT(self, valid_cards, min_visits, is_opponent, constant = 0.7):
#         '''
#         Selection policy for chosing a node in the tree

#         Parameters:
#         valid_cards Card[]: List of cards availible to use in current determinization of the game
#         constant float: used for deriving the statistic

#         Returns:
#         selected_child Node: Node with the highest selection policy value
#         '''
#         explorable_children = []
#         child_cards = [child.last_card for child in self.children]
#         if self.parent == None:
#             for child in self.children:
#                 if child.visits < min_visits: # Asserts that each of root children are visited a set number of times
#                     return child

#         # Gets moves that are possible in current determinization
#         for index, card in enumerate(child_cards):
#             if card in valid_cards:
#                 explorable_children.append(self.children[index])

#         max_conf = float('-inf')
#         min_conf = float('inf')
#         selected_child = None
#         for c in explorable_children: # Selects a node to traverse using UCT selection policy
#             child_conf = c.expected_score + constant*(np.sqrt(np.log(self.visits))/float(c.visits))
#             if not is_opponent and child_conf > max_conf:
#                 max_conf = child_conf
#                 selected_child = c
#             elif is_opponent and child_conf < min_conf:
#                 min_conf = child_conf
#                 selected_child = c
#         return selected_child

    

class Game():
    def __init__(self, players, team_mode=True):
        self.players = players
        self.curr_player_index = 0
        self.teams = [Team(players[0], players[2]), Team(players[1], players[3])]
        self.discard = []
        self.trick = None
        self.turns_remaining = 13
        self.team_mode = team_mode

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
        if self.team_mode: # Case if playing with teams
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
        else: # Case if playing individually
            for player in self.players:
                round_totals = self.get_player_score_and_bags(player.bet, player.tricks)
                player.score += round_totals[0] # Round Score
                player.bags += round_totals[1] # Round Bags
                if player.bags >= 10:
                    player.score -= 100
                    player.bags -= 10
    
    def check_for_winner(self, player_array, threshold = 250):
        '''
        Checks if a player/team has exceed 500 points

        player_array []: Array of either Player or Team depending on game mode

        Returns:
        is_winner bool: True if at least one PLayer/Team exceeds 500 points
        '''
        is_winner = False
        for p in player_array:
            if p.score >= threshold:
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
    def __init__(self, players, curr_player_index, ai_player_index = None, team_mode=True):
        super().__init__(players, team_mode)
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
        clone = SimGame(deepcopy(self.players), deepcopy(self.curr_player_index), deepcopy(self.ai_player_index), self.team_mode)
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
    def __init__(self, players, team_mode = True):
        super().__init__(players, team_mode)
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
        if self.team_mode:
            for index, team in enumerate(self.teams):
                if team.score > highest_score:
                    winning_index = index
                    highest_score = team.score
            print(f"Team {winning_index+1} wins!")
        else:
            for index, player in enumerate(self.players):
                if player.score > highest_score:
                    winning_index = index
                    highest_score = player.score
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
            self.players[i].hand.sort(key=self.sortSuitAndVal) # Sorts player hand
            self.players[i].tricks = 0
            self.players[i].make_bet()
            print(f"Player {i+1} Bet = {self.players[i].bet}")
        self.turns_remaining = 13
        self.play_round(self.curr_player_index)
    
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
        
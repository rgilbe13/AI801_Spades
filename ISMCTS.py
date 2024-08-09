import time
import random
import math
from copy import deepcopy

from Players import Player

class ISMCTSPlayer(Player):
    def __init__(self, iterations):
        super().__init__()
        self.iterations = iterations

    def sortVal(self, e):
        return e.val

    def make_move(self, game):
        '''
        Chooses card to play using ISMCTS

        Parameters:
        game SimGame:copy of the game state up to the MCTS player's intiial turn
        iterations int: number of iterations to run MCTS

        Returns:
        move Card: card to be played in the actual game
        '''
        valid_hand = self.get_valid_cards(game.trick.opening_suit, game.trick.spades_broken)
        if len(valid_hand) > 1: # Only runs MCTS if player has a choice of cards
            root = MCTSNode()
            #self.print_hand()
            start = time.time()
            unseen_cards = self.get_unseen_cards(game) # Cards that are yet to be played from other players
            #iterations = iterations+(int(iterations/2)*(13-game.turns_remaining))
            for _ in range(self.iterations):
                node = root
                clone_game = self.determinize(game.clone_game(), deepcopy(unseen_cards)) # Randomizes non-player hands
                self.MCTS(clone_game, node)
            max_visits = 0
            move = None
            for child in root.children:
                if child.visits > max_visits:
                    max_visits = child.visits
                    move = child.last_card
            end = time.time()
            duration = end-start
            #print(f"Time to make decision: {duration} seconds")
        else:
            move = valid_hand[0]
        self.hand.remove(move)
        return move
    
    def get_unseen_cards(self, game):
        unseen_cards = []
        for p in game.players: # Collects all of the unseen cards
            if p != game.players[game.curr_player_index]:
                for c in p.hand:
                    unseen_cards.append(c)
        return unseen_cards

    def determinize(self, game, unseen_cards):
        '''
        Randomizes the hands of each non-MCTS player

        Parameters:
        game SimGame: copy of the game state up to the MCTS player's intiial turn

        Returns:
        game SimGame: copy of game state with randomized hands
        '''
        random.shuffle(unseen_cards)
        high_value_cards = [card for card in unseen_cards if card.suit == 0 and card.val >= 6 or card.val >= 10] # Gets card with high-trick taking potential
        high_value_count = len(high_value_cards)
        unseen_cards = [card for card in unseen_cards if card not in high_value_cards] # Removes duplicate cards from unseen_cards
        total_bet_difference = 0
        hand_sizes = [0 for _ in range(4)]
        
        # Takes each player's hand size and an estiamte of how many high value cards they are likely to hold
        for index, p in enumerate(game.players):
            if p != game.players[game.curr_player_index]:
                hand_sizes[index] = len(p.hand)
                total_bet_difference += max(0,((p.bet-p.tricks)))
                p.hand = []

        # Deal high value cards based on which players are most likely to have them
        if (total_bet_difference > 0):
            for index, p in enumerate(game.players):
                if p != game.players[game.curr_player_index]:
                    player_bet_difference = max(0, p.bet-p.tricks)
                    high_card_likelihood = player_bet_difference/total_bet_difference
                    cards_to_draw = math.ceil(high_value_count*high_card_likelihood) if math.ceil(high_value_count*high_card_likelihood) < hand_sizes[index] else hand_sizes[index]
                    for _ in range(cards_to_draw):
                        if (len(high_value_cards) > 0):
                            p.hand.append(high_value_cards[0])
                            high_value_cards.pop(0)
        
        if len(high_value_cards) > 0:
            unseen_cards.extend(high_value_cards)
            random.shuffle(unseen_cards)

        # Deals the remainder of the deck
        for index, p in enumerate(game.players): # Inserts randomized cards back into non-player hands
            if p != game.players[game.curr_player_index]:
                hand_remainder = hand_sizes[index]-len(p.hand)
                for _ in range(hand_remainder):
                    p.hand.append(unseen_cards[0])
                    unseen_cards.pop(0) 
        return game

    def MCTS(self, game, node):
        '''
        Implementation of the ISMCTS algorithm, simulates a round and updates node stats

        Parameters:
        game SimGame: copy of the game state up to the MCTS player's intiial turn
        node Node: root of the search tree beginning the the MCTS player's initial turn
        '''

        # Select child nodes up to a leaf or non-fully expanded node
        while len(node.children) > 0:
            valid_cards = game.get_player_valid_cards()
            if node.is_fully_expanded(valid_cards):
                is_opponent = (game.players[game.curr_player_index] not in game.teams[game.ai_team_index].members) # Checks if player is on the AI's team
                node = node.UCT(valid_cards, is_opponent)
                game.play_card(node.last_card)
            else:
                break

        # Expand non-terminal leaf node
        child_cards = [child.last_card for child in node.children]
        valid_cards =  game.get_player_valid_cards()
        valid_cards[:] = [card for card in valid_cards if card not in child_cards]
        if len(valid_cards) > 0:
            probable_card = self.guess_next_card(game, valid_cards)
            child = MCTSNode(node, probable_card, game.players[game.curr_player_index])
            node.children.append(child)
            game.play_card(probable_card)
            node = child

        # Simulate remainder of round
        while (game.turns_remaining) > 0:
            valid_cards = game.get_player_valid_cards()
            probable_card = self.guess_next_card(game, valid_cards)
            game.play_card(probable_card)
            
        # Backpropigate to root
        while node is not None:
            node.update_node(game)
            node = node.parent
        

    def guess_next_card(self, game, valid_cards):
        '''
        Evaluates a given players hand to logically assess their most likely next move

        Parameters:
        game SimGame: copy of the current game state
        valid_cards Card[]: Array of Cards that a player can legally play

        Returns:
        Card: The most beneficial card a player can play based on a series of conditions
        '''
        trick_suit = game.trick.opening_suit
        current_player = game.players[game.curr_player_index]
        cards_in_trick = [card for card in game.trick.cards if card is not None]
        suits_in_hand = [card for card in valid_cards if card.suit == trick_suit] # Cards in player hand that match trick suit
        spades_in_trick = []
        spades_in_hand = []
        if trick_suit != 0:
            spades_in_trick = [card for card in game.trick.cards if card is not None and card.suit == 0]
            spades_in_hand = [card for card in valid_cards if card.suit == 0] # Cards in player hand that are spades
        
        # Case if cards have been played in the trick
        if len(cards_in_trick) > 0:

            # Case for regular bets
            if (current_player.bet != 0):

                # Checks if a playing a spade is possible
                if len(spades_in_hand) > 0 and trick_suit != 0:
                    if len(spades_in_trick) > 0: # Checks if a spade has already been played
                        highest_spade = max(spades_in_hand, key=lambda card: card.val)
                        if highest_spade.val > max(spades_in_hand, key=lambda card: card.val).val: 
                            return highest_spade
                    return min(spades_in_hand, key=lambda card: card.val)
                
                # Checks if player has suits matching the trick
                elif len(suits_in_hand) > 0: 
                    highest_card_of_trick = max(cards_in_trick, key=lambda card: card.val and card.suit == trick_suit and card is not None)
                    max_of_suit = max(suits_in_hand, key=lambda card: card.val)
                    min_of_suit = min(suits_in_hand, key=lambda card: card.val)
                    if max_of_suit.val > highest_card_of_trick.val and len(spades_in_trick) == 0: # Checks if player can take the trick
                        return max_of_suit
                    else:
                        return min_of_suit
                    
                # Checks if player has no spades or matching suits
                else: 
                    valid_cards.sort(key=self.sortVal)
                    return valid_cards[0] # Returns lowest value of another suit

            # Case for nil bets
            else:
                # Checks if a spade can be safely discarded
                if len(spades_in_trick) > 0 and len(spades_in_hand) > 0:
                    highest_spade_of_trick = max(spades_in_trick, key=lambda card: card.val)
                    highest_spade = max(spades_in_hand, key=lambda card: card.val)
                    if highest_spade.val < highest_spade_of_trick.val:  # Checks if highest spade can be safely discarded
                        return highest_spade
                    spades_less_than_max = [spade for spade in spades_in_hand if spade.val < highest_spade_of_trick.val]
                    if len(spades_less_than_max) > 0: # Plays the highest spade card that is guarenteed to not win trick
                            return max(spades_less_than_max, key=lambda card: card.val)
                
                # Checks if a card of the same suit can be discarded
                if len(suits_in_hand) > 0:
                    highest_card_of_trick = max(cards_in_trick, key=lambda card: card.val and card.suit == trick_suit and card is not None)
                    max_of_suit = max(suits_in_hand, key=lambda card: card.val)
                    if (max_of_suit.val < highest_card_of_trick.val) or len(spades_in_trick) > 0: # Plays highest card if its less than the leading trick card
                        return max_of_suit
                    else:
                        suits_less_than_max = [suit for suit in suits_in_hand if suit.val < highest_card_of_trick.val]
                        if len(suits_less_than_max) > 0: # Otherwise lays the highest card that is guarenteed to not win trick
                            return max(suits_less_than_max, key=lambda card: card.val)
                
                # Returns highest value of another suit to be safely discarded
                valid_cards.sort(key=self.sortVal)
                return valid_cards[-1] 
        
        # Case if player is first to play card
        else:
            valid_cards.sort(key=self.sortVal)
            if (current_player.bet != 0): 
                return valid_cards[-1] # Plays highest value card in valid cards
            else:
                return valid_cards[0] # Minimizes chance of winning trick with low val card


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

    
    def update_node(self, game, constant = 500):
        '''
        Updates travseral statistics of node

        Parameters:
        game SimGame: A copy of the current game state
        constant float: used for deriving the statistic
        '''
        self.visits += 1
        highest_score = highest_score_index = 0
        ai_player = game.players[game.ai_player_index]
        for index, player in enumerate(game.players):
            if player != ai_player:
                if player.score > highest_score:
                    highest_score = player.score
                    highest_score_index = index
        opp_player = game.players[highest_score_index]
        self.score_sum += ((ai_player.score-10*ai_player.bags)-(opp_player.score-10*opp_player.bags))/constant
        self.expected_score = self.score_sum/self.visits # Takes the average of all score outcomes


    def UCT(self, valid_cards, is_opponent, constant = 0.7):
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
       
        # Gets moves that are possible in current determinization
        for index, card in enumerate(child_cards):
            if card in valid_cards:
                explorable_children.append(self.children[index])

        max_conf = float('-inf')
        min_conf = float('inf')
        selected_child = None
        for c in explorable_children: # Selects a node to traverse using UCT selection policy
            child_conf = c.expected_score + constant*(math.sqrt(math.log(self.visits))/float(c.visits))
            if not is_opponent and child_conf > max_conf:
                max_conf = child_conf
                selected_child = c
            elif is_opponent and child_conf < min_conf:
                min_conf = child_conf
                selected_child = c
        return selected_child
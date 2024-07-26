import random
from copy import deepcopy

from Card import Card


class Player:

    def __init__(self):
        self.hand = []
        self.legal_moves = []
        self.bet = 0
        self.tricks = 0
        self.bags = 0
        self.score = 0

        # Used for clearly displaying the cards
        self.suit_dict = {0: '♠', 1: '♣', 2: '♥', 3: '♦'}
        self.val_dict = {0: '2', 1: '3', 2: '4', 3: '5',
                4: '6', 5: '7', 6: '8', 7: '9',
                8: '10', 9: 'J', 10: 'Q', 11: 'K',
                12: 'A'}

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

    def __eq__(self, other):
        if not isinstance(other, Player):
            return NotImplemented
        return self.hand == other.hand
    
    def sortSuitAndVal(self, e):
        return e.suit, e.val
    
    def make_bet(self):
        '''
        Evaluates hand and given PT to make a viable bet
        '''
        nil_bet = False
        expected_tricks = self.evaluate_regular_bet()
        if expected_tricks == 1 and Card(0, 12) not in self.hand:
            nil_bet = self.evaluate_nil_bet()
        self.bet = 0 if nil_bet else expected_tricks


    def evaluate_regular_bet(self):
        '''
        Iterates through the different suits to determine the expected trick take

        Returns:
        round(expected_tricks) int: The number of tricks expected to be taken with current hand
        '''
        expected_tricks = 0
        for i in range(4):
            suit_arr = [card for card in self.hand if card.suit == i]
            suit_arr.reverse()
            suit_count = len(suit_arr)
            if i == 0: # Case for evaluating Spades
                high_value_spades = [card for card in suit_arr if card.val >= 9] # Only concerned with spades of val J-A
                for index, card in enumerate(high_value_spades):
                    higher_value_cards = abs(12 - card.val)
                    # The J-Q-K-A spades are each worth a trick if there are more spades in hand than number of un-owned higher-ranked spades
                    if (suit_count > higher_value_cards-index): # Subtract number of higher owned cards
                        expected_tricks+=1
                if suit_count >= 5: # Add a trick for every spade in hand over the fourth
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
        return round(expected_tricks) if round(expected_tricks) > 0 else 1

    def evaluate_nil_bet(self):
        '''
        Checks if a nil bet is a viable choice

        Returns:
        bool: True if a nil bet is deemed to be a low risk option
        '''
        for i in range(4):
            suit_arr = [card for card in self.hand if card.suit == i]
            if len(suit_arr) > 0:
                suit_arr.reverse()
                if i == 0 and suit_arr[0].val > 8: # Ensures we don't nil bet with a face value spade
                    return False
                last_three = suit_arr[-3:] # Gets the three lowest value cards for the given suit
                if len(last_three) > 0 and last_three[0].val > 8: # Checks if the suit hand is 'unsafe' (Bottom 3 value cards contain J or greater)
                    return False
        # print('ATTEMPTING NIL')
        return True
    
    
    def make_move(self):
        pass
    
    def print_hand(self):
        print("[", end=" ")
        for card in self.hand:
            print(f"{self.val_dict[card.val]}-{self.suit_dict[card.suit]}" , end = " ")
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
        valid_hand.sort(key=self.sortSuitAndVal)
        return valid_hand
    
class HumanPlayer(Player):

    def __init__(self):
        super().__init__()

    def make_bet(self):
        self.tricks = 0 # Resets trick count before each new round
        for card in self.hand:
            print(f"{self.val_dict[card.val]}-{self.suit_dict[card.suit]}" , end = " ")
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
            print(f"{index}. {self.val_dict[card.val]}-{self.suit_dict[card.suit]}" , end = " ")
        print("")
        selected_index = int(input("Select a card to play:"))
        while not isinstance(selected_index, int) or selected_index < 0 or selected_index >= len(valid_hand):
            selected_index = int(input("Choose a valid card:"))
        selected_card = valid_hand[selected_index]
        self.hand.remove(selected_card)
        return selected_card
    
    
class RandomPlayer(Player):
    def __init__(self):
        super().__init__()

    def make_move(self, trick):
        valid_hand = self.get_valid_cards(trick.opening_suit, trick.spades_broken)
        selected_card = random.choice(valid_hand)
        self.hand.remove(selected_card)
        return selected_card
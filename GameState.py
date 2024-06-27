
from enum import Enum

class Phase(Enum):
    BID = 1
    HAND = 2
    SCORE = 3

class Trick:
    def __init__(self):
        self.cards_played = []
        self.leading_suit = None
        self.winning_card = None
        self.winning_player = None


class GameState:
    def __init__(self, players):
        self.players = players
        # TODO: May want to rethink how card/suits are paired. Instead of using separate.
        # Maybe use 1-52, 1-13=Spades, 14-27=Hearts, etc.
        self.current_trick = {
            "cards_played": [], # suit_dict
            "leading_suit": None, # suit_dict
            "winning_card": None, # val_dict
            "winning_player": None # Player class
        }
        self.trick_history = [] # Trick class
        self.turn = None # Player 
        self.dealer = None # Player
        self.trick_count = 0 
        self.phase = Phase.BID  # or "playing" or "scoring"
        self.trump = 0 # suit_dcit 0 = Spades

    def play_card(self, player_name, card):
        # Update the current trick with the played card
        self.current_trick['cards_played'].append({"player": player_name, "card": card})
        # If it's the first card, set the leading suit
        if len(self.current_trick['cards_played']) == 1:
            self.current_trick['leading_suit'] = card[-1]
        # Determine the winning card and player so far
        # Can prob use evaluate round from the Game class
        self.evaluate_round()

    def evaluate_round(self):
        # Use or copy from Game class
        pass

    def end_trick(self):
        # Move the current trick to the trick history
        self.trick_history.append(self.current_trick)
        self.current_trick = {
            "cards_played": [],
            "leading_suit": None,
            "winning_card": None,
            "winning_player": None
        }
        self.trick_count += 1

# TODO: def bidding method and move phase
# TODO: def declaring trump method
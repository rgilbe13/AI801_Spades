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
        self.cards = [None for _ in range(4)]
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
import random

class Card:
    
    def __init__(self,suit,val):
        self.suit = suit
        self.val = val
	
    def print_card(self):
	    print(f"{suit_dict[self.suit]}-{val_dict[self.val]}", end=", ")
	       
	        
class Player:

    def __init__(self):
        self.hand = []
        self.legal_moves = []
        self.bet = 0
        self.tricks = 0
        self.bags = 0
        self.score = 0

    def make_bet():
        pass
    
    def make_move(self):
        pass
    
    def print_hand(self):
        pass
    
class HumanPlayer(Player):

    def __init__(self):
        super().__init__()

    def make_bet(self):
        for card in self.hand:
            print(f"{val_dict[card.val]}-{suit_dict[card.suit]}" , end = " ")
        print("")
        bet = int(input("Bet how many tricks you expect to win:"))
        while not isinstance(bet, int) or bet < 0 or bet > 13:
            bet = int(input("Please make a bet between 0 and 13"))
        self.bet = bet
	
    def make_move(self):
        print("Player Move!")
        valid_hand = get_valid_cards(self.hand)
        for index, card in enumerate(valid_hand):
            print(f"{index}. {val_dict[card.val]}-{suit_dict[card.suit]}" , end = " ")
        print("")
        selected_index = int(input("Select a card to play:"))
        while not isinstance(selected_index, int) or selected_index < 0 or selected_index >= len(valid_hand):
            selected_index = int(input("Choose a valid card:"))
        selected_card = valid_hand[selected_index]
        selected_card.print_card()
        self.hand.remove(selected_card)
        if selected_card.suit == 0:
            spades_broken = True
        return selected_card
    
    
class AIPlayer(Player):
    def __init__(self):
        super().__init__()

    def make_bet(self):
        self.bet = random.randint(1,8)

    def make_move(self):
        valid_hand = get_valid_cards(self.hand)
        selected_card = random.choice(valid_hand)
        selected_card.print_card()
        self.hand.remove(selected_card)
        if selected_card.suit == 0:
            spades_broken = True
        return selected_card

p1 = HumanPlayer()
p2 = AIPlayer()
p3 = AIPlayer()
p4 = AIPlayer()
players = [p1, p2, p3, p4]
deck = []
played_suit = -1
spades_broken = False

suit_dict = {0: 'Spade', 1: 'Club', 2: 'Heart', 3: 'Diamond'}
val_dict = {0: '2', 1: '3', 2: '4', 3: '5',
            4: '6', 5: '7', 6: '8', 7: '9',
            8: '10', 9: 'J', 10: 'Q', 11: 'K',
            12: 'A'}

def create_deck():
    for s in range(4):
        for v in range(13):
            deck.append(Card(s,v))
            #deck[-1].print_card()
            
def shuffle():
    random.shuffle(deck)
    
def deal_hand(hand):
    for i in range(13):
        card = deck.pop()
        hand.append(card)

def myFunc(e):
    return e.suit

def get_valid_cards(hand):
    valid_hand = []
    for card in hand:
        # Returns hand of cards that match first played suit (or all but spades if first turn)
        if (card.suit == played_suit or (played_suit == -1 and card.suit != 0) or (played_suit == -1 and spades_broken)):
            valid_hand.append(card)
    if len(valid_hand) == 0: # Returns total hand if player can't match played suit
        valid_hand = hand
    valid_hand.sort(key=myFunc)
    return valid_hand


def play_round(starting_player):
    global played_suit
    global spades_broken
    played_suit = -1 # Resets suit for new round
    spades_broken = False
    trick = [0 for i in range(4)]
    index = players.index(starting_player)
    # Plays turn for each of the four players
    for i in range(4):
        played_card = players[index].make_move()
        if played_suit == -1:
            played_suit = played_card.suit # Sets played_suit to suit of first played card
        trick[index] = played_card
        index+=1 
        if index+1 > len(players):
            index = 0
    winner_index = evaluate_round(trick)
    players[winner_index].tricks += 1
    print(f"Player {winner_index+1} wins the trick! ({val_dict[trick[winner_index].val]}-{suit_dict[trick[winner_index].suit]})")
    if len(players[winner_index].hand) > 0:
        play_round(players[winner_index])

def evaluate_round(trick):
    global played_suit
    highest_val = 0
    winning_player = 0
    for index, card in enumerate(trick):
        if card.suit == played_suit and card.val > highest_val: # Checks if same suit card is the highest value
            highest_val = card.val
            winning_player = index
        elif card.suit == 0 and card.val > highest_val: # Checks if highest value spade has been played
            highest_val = card.val
            winning_player = index
            played_suit = 0
    return winning_player

def award_points():
    is_winner = False
    for index, player in enumerate(players):
        if player.tricks < player.bet:
            player.score -= player.bet*10
        else:
            player.score += player.bet*10
            if player.tricks > player.bet:
                player.bags += player.tricks-player.bet
                if player.bags >= 10:
                    player.score -= 100
                    player.bags -= 10
            if player.score > 500:
                print(f"Player {index+1} wins!")
                is_winner = True
                break
        print(f"Player {index+1} score = {player.score}")
    if is_winner == False:
        start_game()

def start_game():
    create_deck()
    shuffle()
    for i in range(4):
        deal_hand(players[i].hand)
        players[i].make_bet()
    play_round(players[0])
    award_points()

            
start_game()

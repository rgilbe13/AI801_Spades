import random


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
    
    def get_valid_cards(self, hand, first_played_suit, spades_broken):
        '''
        Returns the array of eligible cards (moves) a player has

        Parameters:
        hand Card[]: a list of cards held by some player

        Returns:
        valid_hand Card[]: a pruned version of hand containing only the cards that can currently be played
        '''
        valid_hand = []
        for card in hand:
            # Returns hand of cards that match first played suit (or all but spades if first turn)
            if (card.suit == first_played_suit or (first_played_suit == -1 and card.suit != 0) or (first_played_suit == -1 and spades_broken)):
                valid_hand.append(card)
        if len(valid_hand) == 0: # Returns total hand if player can't match played suit
            valid_hand = hand
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
	
    def make_move(self, first_played_suit, spades_broken):
        print("Player Move!")
        valid_hand = self.get_valid_cards(self.hand, first_played_suit, spades_broken) # Gets array of eligible cards to play
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
        self.bet = random.randint(1,8)

    def make_move(self, first_played_suit, spades_broken):
        valid_hand = self.get_valid_cards(self.hand, first_played_suit, spades_broken)
        selected_card = random.choice(valid_hand)
        self.hand.remove(selected_card)
        return selected_card

class Team:
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.team_members = [p1, p2]
        self.bags = 0
        self.score = 0
        
class Game:
    def __init__(self, p1, p2, p3, p4, mode=False):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.team1 = Team(p1, p3)
        self.team2 = Team(p2, p4)
        self.team_mode = mode
        self.players = [p1, p2, p3, p4]
        self.teams = [self.team1, self.team2]

    deck = []
    played_suit = -1
    spades_broken = False
   

    def create_deck(self):
        '''
        Creates and adds 52 unique card objects to the deck
        '''
        for s in range(4):
            for v in range(13):
                self.deck.append(Card(s,v))
                #deck[-1].print_card()
            
    def shuffle(self):
        '''
        Randomizes the deck order
        '''
        random.shuffle(self.deck)
    
    def deal_hand(self, hand):
        '''
        Deals 13 cards to each player, removing them from the deck
        '''
        for i in range(13):
            card = self.deck.pop()
            hand.append(card)

    def play_hand(self, starting_player):
        '''
        Plays a hand of Spades, giving each player a turn to play a card

        Parameters:
        starting_player Player: Indicates which player plays the first card
        '''
        self.first_played_suit = -1 # Resets suit for new round
        self.spades_broken = False
        trick = [0 for i in range(4)] # Array that stores the played cards for each player
        index = self.players.index(starting_player)

        # Plays turn for each of the four players
        for i in range(4):
            played_card = self.players[index].make_move(self.first_played_suit, self.spades_broken)
            print(f"Player {index+1} -> {val_dict[played_card.val]}-{suit_dict[played_card.suit]}")
            if self.first_played_suit == -1: # Sets played_suit to suit of first played card
                self.first_played_suit = played_card.suit 
            if played_card == 0: # Allows spades to played as the opening card if one has been put down
                self.spades_broken = True
            trick[index] = played_card # Places card into the trick pile
            index = (index+1) if (index+1) < len(self.players) else 0 # Updates player index 
        winner_index = self.evaluate_hand(trick, self.first_played_suit)
        self.players[winner_index].tricks += 1
        print(f"Player {winner_index+1} wins the trick! ({val_dict[trick[winner_index].val]}-{suit_dict[trick[winner_index].suit]})")
        print("-----------")
        if len(self.players[winner_index].hand) > 0: # Starts a new round if layers still have cards in their hand
            self.play_hand(self.players[winner_index]) # Winning player begins the new trick
        else:
            self.tally_points() # Tallys points at the end of a round

    def evaluate_hand(self, trick, winning_suit):
        '''
        Determines which card in a given trick has the highest value

        Parameters:
        trick Card[]: Array of the four cards played in a hand

        Returns:
        winning_player int: The index of the winning player in the Game.players array
        '''
        highest_val = 0
        winning_player = 0
        for index, card in enumerate(trick):
            if card.suit == winning_suit and card.val > highest_val: # Checks if same suit card is the highest value
                highest_val = card.val
                winning_player = index
            elif (card.suit == 0 and card.val > highest_val) or (card.suit == 0 and winning_suit != 0): # Checks if highest value spade has been played
                highest_val = card.val
                winning_player = index
                winning_suit = 0 # Sets dominant suit value to Spade if one is played
        return winning_player
    
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
            score, bags = self.awarded_points(bet, tricks)
        return score, bags
    
    def awarded_points(self, bet, tricks):
        '''
        Gives or deducts points from a given player based on their bet and tricks

        Parameters:
        bet int: Number a given player bet at the start of a round
        tricks int: Number of tricks won by a given player

        Returns:
        score int: Updated score of the given player (+- bet*10 depending on if they met their bet)
        bags int: Updated number of bags a player has tallied
        '''
        bags = 0
        if tricks < bet:
            score = bet*10
        else: 
            score = bet*10
            if tricks > bet: # Adds bags to player total if bet was exceeded
                bags = tricks-bet
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
    
    def check_bag_penalty(self, bags):
        '''
        Checks if a player has hit the bag penalty

        Parameters:
        bags int: Number of bages a given player has

        Returns:
        bool: True if at or beyond bag threshold, o.w False
        '''
        if bags >= 10:
            return True
        return False

    def tally_points(self):
        '''
        Tallys points for all players/teams, starts new round if win condition not met by anyone
        '''
        is_winner = False
        if self.team_mode: # Case if playing with teams
            for team in self.teams:
                for player in team.team_members: # Adds each team members score and bag sum to the team score and bag count
                    player_round_totals = self.get_player_score_and_bags(player.bet, player.tricks)
                    team.score += player_round_totals[0] # Round Score
                    team.bags += player_round_totals[1] # Round Bags
                if self.check_bag_penalty(team.bags):
                    team.score -= 100
                    team.bags -= 10
                if self.check_for_winner(team.score):
                    is_winner = True
        else: # Case if playing individually
            for player in self.players:
                round_totals = self.get_player_score_and_bags(player.bet, player.tricks)
                player.score += round_totals[0] # Round Score
                player.bags += round_totals[1] # Round Bags
                if self.check_bag_penalty(player.bags):
                    player.score -= 100
                    player.bags -= 10
                if self.check_for_winner(player.score):
                    is_winner = True
        if is_winner: # Checks each point total once a player reaches the threshold
            self.declare_winner()
        else: # Starts a new round if no winner has been declared
            self.start_round()
    
    def check_for_winner(self, score):
        '''
        Checks if a player has met the win condition

        Parameters:
        score int: Current score of a given player/team

        Returns
        bool: True if score >= 500, o.w False
        '''
        if score >= 500:
            return True
        return False
    
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

    def start_round(self):
        '''
        Creates card deck, deals cards and has players make bets before starting a new round
        '''
        self.create_deck()
        self.shuffle()
        for i in range(4): # Deals 13 cards to each of the four players and makes them place bets
            self.deal_hand(self.players[i].hand)
            self.players[i].hand.sort(key=sortFunc) # Sorts player hand
            self.players[i].make_bet()
        self.play_hand(self.players[0])

    def initialize_game(self):
        '''
        Initializes player and team properties for a new game
        '''
        for player in self.players:
            player.score = player.bags = player.bet = player.tricks = 0
        for team in self.teams:
            team.score = team.bags = team.bet = team.tricks = 0
        self.start_round()
            

p1 = HumanPlayer()
p2 = AIPlayer()
p3 = AIPlayer()
p4 = AIPlayer()  
g = Game(p1,p2,p3,p4)      
g.initialize_game()

from Game import *

p1 = AIPlayer("Tom", "Donkey")
p2 = AIPlayer("Bruce", "Elephant")
p3 = AIPlayer("Randy", "Donkey")
p4 = MINMAXPlayer("Rex", "Elephant")

p1.set_next_player(p2)
p2.set_next_player(p3)
p3.set_next_player(p4)
p4.set_next_player(p1)

def play_game(game):
    state = game.initial
    game.new_game(state)

    for _ in range(4):
        state.current_player.make_bet()
        state.update_current_player(state.current_player.next_player)

    while not game.is_terminal(state):
        print("--Actual Game Loop--")
        player = state.current_player
        
        move = player.make_move(game, state)

        state = game.result(state, move)

play_game(Spades(p1))
from Game import *

p1 = AIPlayer("Tom", "Donkey")
p2 = AIPlayer("Bruce", "Elephant")
p3 = AIPlayer("Randy", "Donkey")
p4 = MINMAXPlayer("Rex", "Elephant")

p1.set_next_player(p2)
p2.set_next_player(p3)
p3.set_next_player(p4)
p4.set_next_player(p1)

game = Spades()
state = GameState(p1)
state.deal_hand()

while not game.is_terminal(state):

    player = state.current_player
    
    move = player.make_move(game, state)
    print(player," played ", move)
    state = game.result(state, move)


print("end")
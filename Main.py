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


while state.teams[0].score < 500 and state.teams[1].score < 500:

    player = state.current_player
    
    move = player.make_move(game, state)

    print(player," played ", move)

    state = game.result(state, move)

print("Rounds: ", state.rounds)
print("Team: ", state.teams[0].members[0].name, "/", state.teams[0].members[1].name, " - Score: ", state.teams[0].score)
print("Team: ", state.teams[1].members[0].name, "/", state.teams[1].members[1].name, " - Score: ", state.teams[1].score)
print("end")
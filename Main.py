from Game import *
import time



def playGame(game, state):
    start_time = time.time()
    while state.teams[0].score < 500 and state.teams[1].score < 500:

        player = state.current_player

        move = player.make_move(game, state)

        print(player," played ", move)

        state = game.result(state, move)

    state.time = time.time() - start_time
    return state        


count = 0
team_0 = 0
team_1 = 0

while(count < 50):
    p1 = AIPlayer("Tom", "Donkey")
    p2 = MINMAXAlphaBetaPlayer("Bruce", "Elephant")
    p3 = AIPlayer("Randy", "Donkey")
    p4 = MINMAXPlayer("Rex", "Elephant")

    p1.set_next_player(p2)
    p2.set_next_player(p3)
    p3.set_next_player(p4)
    p4.set_next_player(p1)
    count =+ 1    
    game = Spades()
    state = GameState(p1)
    state.deal_hand()  

    state = playGame(game, state)  

    print("Rounds: ", state.rounds)
    print("--- %s seconds ---" % state.time)
    print("Team: ", state.teams[0].members[0].name, "/", state.teams[0].members[1].name, " - Score: ", state.teams[0].score)
    print("Team: ", state.teams[1].members[0].name, "/", state.teams[1].members[1].name, " - Score: ", state.teams[1].score)

    if state.teams[0].score > state.teams[1].score:
        team_0 += 1
    else:
        team_1 += 1

    del game
    del state

print("rounds Played: ", count, " -- Team 0 Total: ", team_0, " - Team 1 Total: ", team_1)
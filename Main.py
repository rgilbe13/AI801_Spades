from Game import *
import time
import csv

def writeToCSV(state, team_0_name, team_1_name):
    # global_search_depth, global_max_depth, team 0, team 0 bid, team 0 score, team 1, team 1 bid, team 1 score, num of rounds, total time
    
    new_data = [
    [global_search_depth, global_max_score, team_0_name, state.teams[0].bet, state.teams[0].tricks, state.teams[0].score, team_1_name, state.teams[1].bet, state.teams[1].tricks, state.teams[1].score, state.rounds, state.time]
    ]

    file_path = "depth_test_" + str(global_search_depth) + ".csv"
    #file_path = "depth_12.csv"

    # Append data to CSV file
    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(new_data)



def playGame(game, state):
    start_time = time.time()
    while state.teams[0].score < global_max_score and state.teams[1].score < global_max_score:
        
        if state.cards_laid == 52:
            state.end_round()     

        player = state.current_player

        move = player.make_move(game, state)

        #print(player," played ", move)   

        state = game.result(state, move)

    state.time = time.time() - start_time
    return state        


count = 0
team_0 = 0
team_1 = 0
team_0_name = None
team_1_name = None

while(count < global_round_count):
    p1 = AIPlayer("Tom", "Donkey")
    p2 = MINMAXAlphaBetaDepthPlayer("Bruce", "Elephant")
    p3 = AIPlayer("Randy", "Donkey")
    p4 = MINMAXAlphaBetaDepthPlayer("Rex", "Elephant")

    p1.set_next_player(p2)
    p2.set_next_player(p3)
    p3.set_next_player(p4)
    p4.set_next_player(p1)
    count += 1    
    game = Spades()
    state = GameState(p1)
    state.new_game()
    total_time = 0;  

    state = playGame(game, state)  
    total_time += state.time

    if state.teams[0].score > state.teams[1].score:
        team_0 += 1
    else:
        team_1 += 1

    team_0_name = state.teams[0].members[0].name + "/" + state.teams[0].members[1].name
    team_1_name = state.teams[1].members[0].name  + "/" + state.teams[1].members[1].name

    writeToCSV(state, team_0_name, team_1_name)

    del game
    del state

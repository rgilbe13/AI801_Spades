import time

from Game import MainGame
from Players import HumanPlayer, RandomPlayer
from ISMCTS import ISMCTSPlayer
from Minimax.All import MINMAXAlphaBetaPlayer


p1 = RandomPlayer()
#p1 = MINMAXAlphaBetaPlayer("p1", "T1")
p2 = ISMCTSPlayer(100)
p3 = RandomPlayer()
p3 = MINMAXAlphaBetaPlayer("p3", "T1")
p4 = ISMCTSPlayer(100)  

p1.set_next_player(p2)
p2.set_next_player(p3)
p3.set_next_player(p4)
p4.set_next_player(p1)

g = MainGame([p1,p2,p3,p4])  

games_played = 0
mcts_wins = 0
random_wins = 0
start_test = time.time()
for i in range(50):
    g.initialize_game()
    games_played += 1
    if g.teams[0].score > g.teams[1].score:
        random_wins += 1
        print(f'Random Player: {random_wins}/{games_played}')
    else:
        mcts_wins += 1
        print(f'MCTS Player: {mcts_wins}/{games_played}')

end_test = time.time()
elapsed = end_test-start_test
print("Finished!")
print(f"MCTS: {mcts_wins} ({mcts_wins/games_played})")
print(f"Random: {random_wins} ({random_wins/games_played})")
print(elapsed)

f = open("Spades_Results_5000.txt", "a")
f.write(f"MCTS player wins: {mcts_wins} (Win%: {mcts_wins/games_played}) \n")
f.write(f"Random player wins: {random_wins} (Win%: {random_wins/games_played}) \n")
f.write(f"{elapsed} seconds to completion")
f.close()
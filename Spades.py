import time

from Game import MainGame
from Players import HumanPlayer, RandomPlayer
from ISMCTS import ISMCTSPlayer


p1 = RandomPlayer()
p2 = ISMCTSPlayer()
p3 = RandomPlayer()
p4 = ISMCTSPlayer()  
g = MainGame([p1,p2,p3,p4], True)   

games_played = 0
mcts_wins = 0
random_wins = 0
start_test = time.time()
for i in range(100):
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

f = open("Spades_Results.txt", "a")
f.write(f"MCTS player wins: {mcts_wins} (Win%: {mcts_wins/games_played}) \n")
f.write(f"Random player wins: {random_wins} (Win%: {random_wins/games_played}) \n")
f.write(f"{elapsed} seconds to completion")
f.close()
# 500 iterations per MCTS
import math
import time
from collections import deque
infinity = math.inf

def alphabeta_breadth_first_search(game, state, is_maximizing_player):
    root = state
    queue = deque([(state, 0)])
    levels = {}  # Dictionary to store nodes at each level

    # Perform BFS to populate levels dictionary
    while queue:
        state, level = queue.popleft()
        if level not in levels and level < 12:
            levels[level] = []
        levels[level].append(state)
        for action in game.actions(state):
            queue.append((game.result(state, action), level + 1))

    # Evaluate leaf nodes
    max_level = max(levels.keys())
    for state in levels[max_level]:
        state.value = game.utility(state, state.current_player)

    # Backpropagate values from leaves to root
    for level in range(max_level - 1, -1, -1):
        for state in levels[level]:
            if is_maximizing_player:
                state.value = max(game.result(state, action) for action in game.actions(state))
                state.best_play = action
            else:
                state.value = min(game.result(state, action) for action in game.actions(state))
                state.best_play = action
            is_maximizing_player = not is_maximizing_player

    return root.value, root.best_move
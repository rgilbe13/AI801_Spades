import math
import time
infinity = math.inf

search_depth = 0
max_depth = 3000

def minimax_search(game, state):
    global search_depth
    
    def max_value(state):
        global search_depth
        search_depth += 1
        #time.sleep(2)
        if game.is_terminal(state) or search_depth > 3000:
            return game.utility(state, state.current_player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a))
            if v2 > v:
                v, move = v2, a
        return v, move

    def min_value(state):
        global search_depth
        search_depth += 1
        #time.sleep(2)
        if game.is_terminal(state) or search_depth > 3000:
            return game.utility(state, state.current_player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a))
            if v2 < v:
                v, move = v2, a
        return v, move
    search_depth = 0
    return max_value(state)
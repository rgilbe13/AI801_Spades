import math
import time
infinity = math.inf

search_depth = 0

def alphabeta_search(game, state):
    global search_depth
    player = state.to_move

    def max_value(state, alpha, beta):
        global search_depth
        search_depth += 1
        if game.is_terminal(state) or search_depth > 100:
            return game.utility(state, state.current_player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    def min_value(state, alpha, beta):
        global search_depth
        search_depth += 1
        if game.is_terminal(state) or search_depth > 100:
            return game.utility(state, state.current_player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), alpha, beta)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move
    
    search_depth = 0
    return max_value(state, -infinity, +infinity)
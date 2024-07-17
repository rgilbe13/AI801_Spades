import math
import time
infinity = math.inf



def minimax_search(game, state):
    search_depth = 0
    def max_value(state, search_depth):
        search_depth = search_depth + 1
        print("Depth: ", search_depth)
        #time.sleep(2)
        if game.is_terminal(state):
            print("--Max UTILITY-- ",  game.utility(state, state.current_player))
            return game.utility(state, state.current_player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), search_depth)
            if v2 > v:
                v, move = v2, a
        return v, move

    def min_value(state, search_depth):
        search_depth = search_depth + 1
        print("Depth: ", search_depth)
        #time.sleep(2)
        if game.is_terminal(state):
            print("--Min UTILITY-- ",  game.utility(state, state.current_player))
            return game.utility(state, state.current_player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), search_depth)
            if v2 < v:
                v, move = v2, a
        return v, move

    return max_value(state, search_depth)
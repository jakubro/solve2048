import logging
import math
import operator
from typing import Any, TypeVar

import game

T_Action = TypeVar('T_Action')
T_Game = game.Game[Any, int, T_Action]

_log = logging.getLogger()


def minimax_decision(game_: T_Game) -> T_Action:
    if game_.player == -1:
        utility = max_value
        result = min
    else:
        assert game_.player == +1
        utility = min_value
        result = max

    utilities = []
    for a in game_.actions():
        ply = game_.invoke(a)
        v = utility(ply, -math.inf, +math.inf)
        utilities.append((a, v))

    rv, _ = result(utilities, operator.itemgetter(1))
    return rv


def min_value(game_: T_Game, alpha: float, beta: float) -> float:
    if game_.terminal_test():
        return game_.utility()

    rv = +math.inf
    for a in game_.actions():
        ply = game_.invoke(a)
        rv = min(rv, max_value(ply, alpha, beta))
        if rv <= alpha:
            return rv
        beta = min(beta, rv)
    return rv


def max_value(game_: T_Game, alpha: float, beta: float) -> float:
    if game_.terminal_test():
        return game_.utility()

    rv = -math.inf
    for a in game_.actions():
        ply = game_.invoke(a)
        rv = max(rv, min_value(ply, alpha, beta))
        if rv >= beta:
            return rv
        alpha = max(alpha, rv)
    return rv

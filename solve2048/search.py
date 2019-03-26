import logging
import math
import operator
from typing import Any, TypeVar

import game

T_Action = TypeVar('T_Action')
T_Game = game.Game[Any, int, T_Action]

_log = logging.getLogger()


def minimax_decision(game_: T_Game) -> T_Action:
    if is_min(game_):
        utility = max_value
        result = min
    else:
        assert is_max(game_)
        utility = min_value
        result = max

    utilities = []
    for a in game_.actions():
        ply = game_.invoke(a)
        v = utility(ply)
        utilities.append((a, v))
    return result(utilities, operator.itemgetter(1))


def is_min(game_: T_Game) -> bool:
    return game_.player == -1


def is_max(game_: T_Game) -> bool:
    return game_.player == +1


def min_value(game_: T_Game) -> float:
    if game_.terminal_test():
        return game_.utility()
    v = +math.inf
    for a in game_.actions():
        ply = game_.invoke(a)
        v = min(v, max_value(ply))
    return v


def max_value(game_: T_Game) -> float:
    if game_.terminal_test():
        return game_.utility()
    v = -math.inf
    for a in game_.actions():
        ply = game_.invoke(a)
        v = max(v, min_value(ply))
    return v

import logging
import math
import operator
import random
from typing import Any, Callable, Dict, List, Optional, Tuple

import cache
import game

T_Game = game.Game[Any, int]

_log = logging.getLogger()


# Expectimax
# -----------------------------------------------------------------------------

# @cache.cached()
def expectimax_decision(game_: T_Game,
                        depth: int = -1,
                        alpha=-math.inf,
                        beta=+math.inf) -> Dict[str, Any]:
    try:
        actions = game_.actions()
        if not actions:
            raise StopIteration()

        if game_.player == -1:
            return random.choice(actions)
        else:
            assert game_.player == +1

            utilities = []
            for a in actions:
                ply = game_.invoke(**a)
                v = _expectimax_chance_value(ply, depth=depth)
                _log.debug(f"{a}\tUtility: {v:.2f}")
                utilities.append((a, v))

            # Choose action with best utility if there was not a tie in the 
            # expected utilities, otherwise do iterative deepening provided
            # that we're still within reasonable bounds (alpha, beta).

            rv = _best_utility(utilities, operator.gt)
            if rv is not None:
                return rv
            a, v = utilities[0]
            if v <= alpha or v >= beta:
                return a
            return expectimax_decision(game_, depth + 1)
    finally:
        _log.debug(cache.get_stats())
        cache.reset_stats(module='rules')


@cache.cached()
def _expectimax_max_value(game_: T_Game, depth: int = -1) -> float:
    assert game_.player == +1

    if game_.terminal_test() or depth == 0:
        return game_.utility()

    rv = -math.inf
    for a in game_.actions():
        ply = game_.invoke(**a)
        rv = max(rv, _expectimax_chance_value(ply, depth=depth - 1))
    return rv


@cache.cached()
def _expectimax_chance_value(game_: T_Game, depth: int = -1) -> float:
    assert game_.player == -1

    if game_.terminal_test() or depth == 0:
        return game_.utility()

    rv = 0
    actions = game_.actions()
    for a in actions:
        ply = game_.invoke(**a)
        rv += _expectimax_max_value(ply, depth=depth - 1)
    return rv / len(actions)


# Minimax
# -----------------------------------------------------------------------------

# @cache.cached()
def minimax_decision(game_: T_Game,
                     depth: int = -1,
                     alpha=-math.inf,
                     beta=+math.inf) -> Dict[str, Any]:
    try:
        actions = game_.actions()
        if not actions:
            raise StopIteration()

        if game_.player == -1:
            utility = _minimax_max_value
            op = operator.lt
        else:
            assert game_.player == +1
            utility = _minimax_min_value
            op = operator.gt

        utilities = []
        for a in actions:
            ply = game_.invoke(**a)
            v = utility(ply, -math.inf, +math.inf, depth=depth)
            _log.debug(f"{a} {v}")
            utilities.append((a, v))

        # Choose action with best utility if there was not a tie in the 
        # expected utilities, otherwise do iterative deepening provided
        # that we're still within reasonable bounds (alpha, beta).

        rv = _best_utility(utilities, operator.gt)
        if rv is not None:
            return rv
        a, v = utilities[0]
        if v <= alpha or v >= beta:
            return a
        return expectimax_decision(game_, depth + 1)
    finally:
        _log.debug(cache.get_stats())
        cache.reset_stats(module='rules')


@cache.cached()
def _minimax_max_value(game_: T_Game,
                       alpha: float,
                       beta: float,
                       depth: int = -1) -> float:
    assert game_.player == +1

    if game_.terminal_test() or depth == 0:
        return game_.utility()

    rv = -math.inf
    for a in game_.actions():
        ply = game_.invoke(**a)
        rv = max(rv, _minimax_min_value(ply, alpha, beta, depth=depth - 1))
        if rv >= beta:
            return rv
        alpha = max(alpha, rv)
    return rv


@cache.cached()
def _minimax_min_value(game_: T_Game,
                       alpha: float,
                       beta: float,
                       depth: int = -1) -> float:
    assert game_.player == -1

    if game_.terminal_test() or depth == 0:
        return game_.utility()

    rv = +math.inf
    for a in game_.actions():
        ply = game_.invoke(**a)
        rv = min(rv, _minimax_max_value(ply, alpha, beta, depth=depth - 1))
        if rv <= alpha:
            return rv
        beta = min(beta, rv)
    return rv


# Helpers
# -----------------------------------------------------------------------------


def _best_utility(utilities: List[Tuple[Dict[str, Any], float]],
                  cmp: Callable,
                  ) -> Optional[Dict[str, Any]]:
    rv = None
    best = None
    for a, v in utilities:
        if best is None or cmp(v, best):
            best = v
            rv = a
        elif v == best or abs(v - best) <= 0.0001:
            return None

    return rv

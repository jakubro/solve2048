import logging
import math
import operator
import random
from typing import Any, Callable, Dict, List, Tuple

import cache
import game

T_Game = game.Game[Any, int]

_log = logging.getLogger()


# Expectimax
# -----------------------------------------------------------------------------

# @cache.cached()
def expectimax_decision(game_: T_Game, depth: int = -1) -> Dict[str, Any]:
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
                _log.debug(f"{a} {v}")
                utilities.append((a, v))

            return _optimize_immediate_utility(game_, utilities, operator.gt)
    finally:
        for n, o in (('expectimax_decision', expectimax_decision),
                     ('_expectimax_max_value', _expectimax_max_value),
                     ('_expectimax_chance_value', _expectimax_chance_value)):
            try:
                # noinspection PyProtectedMember
                ch = o._cache
            except AttributeError:
                pass
            else:
                hit = ch.hit
                miss = ch.miss
                _log.debug(f"Cache {n}:\t"
                           f"Hit: {hit / (hit + miss) * 100:.2f}%\t"
                           f"Miss: {miss / (hit + miss) * 100:.2f}%")


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
def minimax_decision(game_: T_Game, depth: int = -1) -> Dict[str, Any]:
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

        return _optimize_immediate_utility(game_, utilities, op)
    finally:
        for n, o in (('minimax_decision', minimax_decision),
                     ('_minimax_max_value', _minimax_max_value),
                     ('_minimax_min_value', _minimax_min_value)):
            try:
                # noinspection PyProtectedMember
                ch = o._cache
            except AttributeError:
                pass
            else:
                hit = ch.hit
                miss = ch.miss
                _log.debug(f"Cache {n}:\t"
                           f"Hit: {hit / (hit + miss) * 100:.2f}%\t"
                           f"Miss: {miss / (hit + miss) * 100:.2f}%")


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

def _optimize_immediate_utility(game_: T_Game,
                                utilities: List[Tuple[Dict[str, Any], float]],
                                cmp: Callable) -> Dict[str, Any]:
    # Min/maximize immediate utility, if there's a tie in the expectations.
    best = None
    ties = None
    for a, v in utilities:
        if best is None or cmp(v, best):
            best = v
            ties = [a]
        elif v == best or abs(v - best) <= 0.0001:
            ties.append(a)

    if len(ties) == 1:
        return ties[0]
    else:
        assert len(ties) > 1
        best = None
        rv = None
        for a in ties:
            ply = game_.invoke(**a)
            v = ply.utility()
            if best is None or cmp(v, best):
                best = v
                rv = a
        return rv

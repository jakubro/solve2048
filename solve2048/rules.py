import enum
import math
import random
from typing import Any, Dict, List, Optional, Tuple

import cache
import game

#: Player. -1 for MIN, the AI. +1 for MAX, the actual player.
Player = int

#: Tuple of vertical and horizontal offset from the origin (top, left).
Position = Tuple[int, int]
Size = Position

#: Key is position of this tile on the board.
#: Value is numerical value of the tile. None if the tile is empty.
Board = Dict[Position, Optional[int]]


class Direction(enum.Enum):
    """Direction in which to move all the tile on the board."""

    UP = enum.auto()
    RIGHT = enum.auto()
    DOWN = enum.auto()
    LEFT = enum.auto()


class Game2048(game.Game[Board, Player]):
    """2048 game.

    See https://en.wikipedia.org/wiki/2048_(video_game)
    """

    def __init__(self,
                 state: Board,
                 player: Player,
                 size: Size,
                 terminal_score: int):
        """
        :param state: Initial state.
        :param player: Player ID.
        :param size: Size of the board.
        :param terminal_score: Max score when the game ends.
        """

        super().__init__(state, player)
        self.size = size
        self.terminal_score = terminal_score

    def __hash__(self, *args, **kwargs):
        rv = getattr(self, '__hashvalue', None)
        if rv is None:
            self.__hashvalue = rv = hash((tuple(self.state.items()),
                                          self.player,
                                          self.size,
                                          self.terminal_score))
        return rv

    # Heuristics
    # -------------------------------------------------------------------------

    # @cache.cached()
    def terminal_test(self) -> bool:
        if self.score() >= self.terminal_score:
            return True  # max wins
        if not self.actions():
            return True  # min wins
        return False

    # @cache.cached()
    def score(self) -> float:
        return max(0, *(x for x in self.state.values() if x is not None))

    # @cache.cached()
    def utility(self) -> float:
        if self.score() >= self.terminal_score:
            return self.max_utility()

        if not self.actions():
            return self.min_utility()

        powers = [int(math.log(x or 1, 2)) for _, x in self._board_as_snake()]
        inversions = self._count_inversions(tuple(powers))

        score = self.score()

        return inversions * score  # * log_score

    def _count_inversions(self, arr: tuple) -> int:
        rv = 0
        add = True
        for i, a in enumerate(arr):
            for j, b in enumerate(arr):
                if i < j:
                    if a < b:
                        q = (len(arr) - i) * (len(arr) - j) * b ** 2
                        rv -= q
                        add = False
                if i == j - 1:
                    if a == b + 1:
                        q = (len(arr) - i) * (len(arr) - j) * a ** 2
                        rv += q if add else -q
        return rv

    def min_utility(self) -> float:
        return - (10 ** (math.log(self.terminal_score, 2) + 10))

    def max_utility(self) -> float:
        return 10 ** (math.log(self.terminal_score, 2) + 10)

    # Actions
    # -------------------------------------------------------------------------

    @cache.cached(key=lambda x: x.size)
    def all_actions(self) -> List[Dict[str, Any]]:
        height, width = self.size
        new_tiles = [dict(player=-1, position=(i, j))
                     for i in range(height)
                     for j in range(width)]
        directions = [dict(player=+1, direction=d) for d in Direction]
        return [*new_tiles, *directions]

    @cache.cached()
    def actions(self) -> List[Dict[str, Any]]:
        return super().actions()

    # Can Invoke?
    # -------------------------------------------------------------------------

    @cache.cached()
    def can_invoke(self, **kwargs) -> bool:
        if self.player == -1:
            return self._can_invoke_min(**kwargs)
        else:
            assert self.player == +1
            return self._can_invoke_max(**kwargs)

    def _can_invoke_min(self, **kwargs) -> bool:
        if kwargs['player'] != -1:
            return False
        position: Position = kwargs['position']
        return self.state[position] is None

    def _can_invoke_max(self, **kwargs) -> bool:
        if kwargs['player'] != +1:
            return False
        direction: Direction = kwargs['direction']
        height, width = self.size
        for row in self._rotate_board(height, width, direction):
            previous = Ellipsis  # value of the last visited tile
            previous_non_empty = Ellipsis
            for pos in row:
                current = self.state[pos]
                if current is not None:
                    if previous is None:
                        return True  # empty tiles elimination
                    if current == previous_non_empty:
                        return True  # equal tiles squashing
                    previous_non_empty = current
                previous = current
        return False

    # Invoke
    # -------------------------------------------------------------------------

    @cache.cached()
    def invoke(self, **kwargs) -> 'Game2048':
        if self.player == -1:
            state = self._invoke_min(**kwargs)
        else:
            assert self.player == 1
            state = self._invoke_max(**kwargs)
        return Game2048(state,
                        player=-self.player,
                        size=self.size,
                        terminal_score=self.terminal_score)

    def _invoke_min(self, **kwargs) -> Board:
        if not self.can_invoke(**kwargs):
            raise ValueError('kwargs')

        position: Position = kwargs['position']

        # noinspection PyDictCreation
        state = {**self.state}
        state[position] = 2
        return state

    def _invoke_max(self, **kwargs) -> Board:
        if not self.can_invoke(**kwargs):
            raise ValueError('kwargs')

        direction: Direction = kwargs['direction']

        state = {**self.state}
        self._eliminate_empty_tiles(state, direction)
        self._squash_equal_tiles(state, direction)
        self._eliminate_empty_tiles(state, direction)
        return state

    def _eliminate_empty_tiles(self,
                               state: Board,
                               direction: Direction) -> None:
        """Move non-empty tile along the desired direction, while the empty
        tiles vanish."""

        height, width = self.size
        for row in self._rotate_board(height, width, direction):
            empty = []  # queue of visited empty tiles
            for pos in row:
                current = state[pos]

                if current is None:
                    empty.append(pos)
                elif empty:
                    empty_pos = empty.pop(0)
                    empty.append(pos)
                    state[empty_pos] = current
                    state[pos] = None

    def _squash_equal_tiles(self, state: Board, direction: Direction) -> None:
        """Squashes two tiles of equal value into one tile, which is
        put on the position of the first tile, while the other tile is left
        empty."""

        height, width = self.size
        for row in self._rotate_board(height, width, direction):
            previous = None  # value of the last visited tile
            prev_pos = None  # .. and its position
            for pos in row:
                current = state[pos]

                if current is not None and current == previous:
                    state[prev_pos] = current = previous * 2
                    state[pos] = None

                previous = current
                prev_pos = pos

    # Board Iterators
    # -------------------------------------------------------------------------

    @cache.cached()
    def _board_as_snake(self) -> List[Tuple[Position, int]]:
        # iterate through the board as snake, i.e.
        # 0 1 2
        # 5 4 3
        # 6 7 8

        height, width = self.size
        rv = []
        reverse = False
        for i in range(height):
            start = width - 1 if reverse else 0
            stop = -1 if reverse else width
            step = -1 if reverse else +1
            for j in range(start, stop, step):
                pos = (i, j)
                val = self.state[pos]
                rv.append((pos, val))
            reverse = not reverse
        return rv

    @classmethod
    @cache.cached()
    def _rotate_board(cls,
                      height: int,
                      width: int,
                      direction: Direction) -> List[List[Position]]:
        """
        :param direction: Direction in which to move all the tile on the board.
        :returns: Positions to be iterated from top to left, as if the board
            was rotated in such manner that the desired direction `action`
            points upwards.

        **Example**

        For dimensions (height=2, width=3):

        Action.UP
          (0, 0) (1, 0)
          (0, 1) (1, 1)
          (0, 2) (1, 2)

        Action.RIGHT
          (0, 2) (0, 1) (0, 0)
          (1, 2) (1, 1) (1, 0)

        Action.DOWN
          (1, 0) (0, 0)
          (1, 1) (0, 1)
          (1, 2) (0, 2)

        Action.LEFT
          (0, 0) (0, 1) (0, 2)
          (1, 0) (1, 1) (1, 2)
        """

        r1 = [(x, 0) for x in range(height)]
        r2 = [(0, x) for x in range(width)]

        if direction in (Direction.UP, Direction.DOWN):
            r1, r2 = r2, r1

        if direction in (Direction.RIGHT, Direction.DOWN):
            r2 = list(reversed(r2))

        rv = []
        for i1, j1 in r1:
            rng = []
            for i2, j2 in r2:
                i = i1 + i2
                j = j1 + j2
                rng.append((i, j))
            rv.append(rng)
        return rv

    # Misc
    # -------------------------------------------------------------------------

    def __str__(self):
        height, width = self.size
        tile_width = self._max_tile_width()
        state = self.state
        rv = ""
        for i in range(height):
            rv += "\n"
            for j in range(width):
                it = state[(i, j)]
                it = self._str_tile(it)
                rv += it.center(tile_width)
                rv += " "
        return rv.strip("\n")

    def _max_tile_width(self) -> int:
        """:returns: Width of the widest tile's string representation."""

        state = self.state
        values = [self._str_tile(x) for x in state.values()]
        min_value = self._str_tile(0)
        max_value = max((min_value, *values), key=lambda x: len(str(x)))
        return len(str(max_value))

    def _str_tile(self, value: int) -> str:
        """:returns: String representation of the tile."""

        if value is not None:
            return str(value)
        else:
            return "."

    @classmethod
    def initialize(cls, **kwargs) -> 'Game2048':
        # size of the board
        height, width = kwargs['size']
        state = {(i, j): None for i in range(height) for j in range(width)}
        rv = Game2048(state, player=-1, **kwargs)
        rv = rv.invoke(**random.choice(rv.actions()))
        return rv

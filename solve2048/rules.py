import enum
import math
import random
from typing import Dict, Iterator, List, Optional, Tuple

import game

#: Player. -1 for MIN, the AI. +1 for MAX, the actual player.
Player = int

#: Tuple of vertical and horizontal offset from the origin (top, left).
Position = Tuple[int, int]

#: Key is position of this tile on the board.
#: Value is numerical value of the tile. None if the tile is empty.
Board = Dict[Position, Optional[int]]


class Action(enum.Enum):
    """Direction in which to move all the tile on the board."""

    # min's actions
    NEXT = enum.auto()

    # max's actions
    UP = enum.auto()
    RIGHT = enum.auto()
    DOWN = enum.auto()
    LEFT = enum.auto()


class Game2048(game.Game[Board, Player, Action]):
    """2048 game.

    See https://en.wikipedia.org/wiki/2048_(video_game)
    """

    def __init__(self, state: Board, player: Player, width: int, height: int):
        """
        :param state: Initial state.
        :param width: Width of the board.
        :param height: Height of the board.
        """

        super().__init__(state, player)
        self.width = width
        self.height = height

    def terminal_test(self) -> bool:
        if not self.actions():
            return True  # min wins
        if self._max_score() >= 2048:
            return True  # max wins
        return False

    def utility(self) -> float:
        score = self._max_score()
        if self.terminal_test():
            if score >= 2048:
                return +math.inf
            else:
                return -math.inf
        else:
            return score

    def _max_score(self) -> int:
        # sum of all tiles
        rv = 0
        for v in self.state.values():
            if v is not None:
                rv += v
        return rv

    @classmethod
    def all_actions(cls) -> List[Action]:
        # noinspection PyTypeChecker
        return list(Action)

    def can_invoke(self, action: Action) -> bool:
        if self.player == -1:
            if action != action.NEXT:
                return False
            for v in self.state.values():
                if v is None:
                    return True
            return False
        else:
            assert self.player == +1
            for row in self._rotate_board(action):
                previous = None  # value of the last visited tile
                for pos in row:
                    current = self.state[pos]
                    if current is not None:
                        if previous is None:
                            return True  # empty tiles elimination
                        if current == previous:
                            return True  # equal tiles squashing
                    previous = current
            return False

    def invoke(self, action: Action) -> 'Game2048':
        if not self.can_invoke(action):
            raise ValueError('action')

        state = {**self.state}
        if self.player == -1:
            pos = self._random_empty_position(state, self.width, self.height)
            state[pos] = 2
        else:
            assert self.player == 1
            self._eliminate_empty_tiles(state, action)
            self._squash_equal_tiles(state, action)
            self._eliminate_empty_tiles(state, action)

        return Game2048(state, -self.player, self.width, self.height)

    def _eliminate_empty_tiles(
            self,
            state: Board,
            action: Action,
    ) -> None:
        """Move non-empty tile along the desired direction, while the empty
        tiles vanish."""

        for row in self._rotate_board(action):
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

    def _squash_equal_tiles(self, state: Board, action: Action) -> None:
        """Squashes two tiles of equal value into one tile, which is
        put on the position of the first tile, while the other tile is left
        empty."""

        for row in self._rotate_board(action):
            previous = None  # value of the last visited tile
            prev_pos = None  # .. and its position
            for pos in row:
                current = state[pos]

                if current is not None and current == previous:
                    state[prev_pos] = previous * 2
                    state[pos] = None

                previous = current
                prev_pos = pos

    def _rotate_board(
            self,
            action: Action,
    ) -> Iterator[Iterator[Position]]:
        """
        :param action: Direction in which to move all the tile on the board.
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

        r1 = [(x, 0) for x in range(self.height)]
        r2 = [(0, x) for x in range(self.width)]

        if action in (Action.UP, Action.DOWN):
            r1, r2 = r2, r1

        if action in (Action.RIGHT, Action.DOWN):
            r2 = list(reversed(r2))

        for i1, j1 in r1:
            rng = []
            for i2, j2 in r2:
                i = i1 + i2
                j = j1 + j2
                rng.append((i, j))
            yield iter(rng)

    def __str__(self):
        state = self.state
        rv = ""
        for i in range(self.height):
            rv += "\n"
            for j in range(self.width):
                it = state[(i, j)]
                rv += str(it) if it is not None else "-"
                rv += " "
        return rv.strip("\n")

    @classmethod
    def initialize(cls, **kwargs) -> 'Game2048':
        width = kwargs.get('width')
        height = kwargs.get('height')
        state = {(i, j): None for i in range(height) for j in range(width)}
        rv = Game2048(state, -1, **kwargs)
        rv = rv.invoke(Action.NEXT)
        return rv

    @classmethod
    def _random_empty_position(
            cls,
            state: Board,
            width: int,
            height: int,
    ) -> Optional[Position]:
        empty = []
        for i in range(height):
            for j in range(width):
                pos = (i, j)
                if state[pos] is None:
                    empty.append(pos)

        if not empty:
            return None

        x = random.randint(0, len(empty) - 1)
        return empty[x]

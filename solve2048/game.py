import abc
from typing import Any, Dict, Generic, List, TypeVar

T_State = TypeVar('T_State')
T_Player = TypeVar('T_Player')


class Game(Generic[T_State, T_Player]):
    def __init__(self, state: T_State, player: T_Player):
        """
        :param state: Initial state.
        """

        self._state = state
        self._player = player

    @property
    def state(self) -> T_State:
        """:returns: Current state."""

        return self._state

    @property
    def player(self) -> T_Player:
        """:returns: Player to take action."""

        return self._player

    @abc.abstractmethod
    def terminal_test(self) -> bool:
        """:returns: True if current state if the game is over, otherwise
        False."""

        pass

    @abc.abstractmethod
    def score(self) -> float:
        """:returns: Score for the player in the current state."""

        pass

    @abc.abstractmethod
    def utility(self) -> float:
        """:returns: Utility value for the player in the current state."""

        pass

    @abc.abstractmethod
    def all_actions(self) -> List[Dict[str, Any]]:
        """:returns: List of all actions."""

        pass

    def actions(self) -> List[Dict[str, Any]]:
        """:returns: List of actions applicable for the player in the current
        state."""

        rv = []
        for kwargs in self.all_actions():
            if self.can_invoke(**kwargs):
                rv.append(kwargs)
        return rv

    @abc.abstractmethod
    def can_invoke(self, **kwargs) -> bool:
        """Tests whether the action is applicable for player in the current
        state.

        :param action: Action to test.
        :returns: True if action is applicable for player in the current state,
        otherwise False.
        """

        pass

    @abc.abstractmethod
    def invoke(self, **kwargs) -> 'Game':
        """Invokes action.

        :param action: Action to invoke.
        :returns: Problem, which is transitioned to the new state.

        **Remarks:**

        This method does not alter the `self`. Instead, it returns modified
        game.
        """

        pass

    @classmethod
    @abc.abstractmethod
    def initialize(cls, **kwargs) -> 'Game':
        """:returns: New game."""

        pass

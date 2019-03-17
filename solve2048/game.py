import abc
from typing import Generic, List, TypeVar

T_State = TypeVar('T_State')
T_Action = TypeVar('T_Action')


class Game(Generic[T_State, T_Action]):
    def __init__(self, state: T_State):
        """
        :param state: Initial state.
        """

        self._state = state

    @property
    def state(self) -> T_State:
        """:returns: Current state."""

        return self._state

    @classmethod
    @abc.abstractmethod
    def all_actions(cls) -> List[T_Action]:
        """:returns: List of all actions."""

        pass

    def actions(self) -> List[T_Action]:
        """:returns: List of actions applicable in the current state."""

        rv = []
        for action in self.all_actions():
            if self.can_invoke(action):
                rv.append(action)
        return rv

    @abc.abstractmethod
    def can_invoke(self, action: T_Action) -> bool:
        """Tests whether the action is applicable in the current state.

        :param action: Action to test.
        :returns: True if action is applicable in the current state,
        otherwise False.
        """

        pass

    @abc.abstractmethod
    def invoke(self, action: T_Action) -> 'Game':
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

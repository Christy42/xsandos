from abc import abstractmethod
from copy import deepcopy


class Game:
    def __init__(self):
        # Some games may not have a board but that can be changed later
        self._board = []
        self._pieces = {}  # May not be needed for a game but can be ignored
        self._next_player = None

    def copy(self, include_history=True):
        pass

    @property
    def pieces(self):
        return self._pieces

    @abstractmethod
    def print_board(self):
        pass

    @property
    def board(self):
        return self._board

    @property
    def next_player(self):
        return self._next_player

    @abstractmethod
    def possible_moves(self, **kwargs):
        pass

    @abstractmethod
    def check_end_game(self, **kwargs):
        pass

    @abstractmethod
    def make_move(self, move):
        pass

    @abstractmethod
    def check_move(self, move):
        pass


class GameRunner:
    def __init__(self):
        self._game = None

    @abstractmethod
    def start_game(self):
        pass

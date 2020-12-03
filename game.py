from abc import abstractmethod
from copy import deepcopy


class Game:
    def __init__(self):
        # Some games may not have a board but that can be changed later
        self._board = []
        self._ais = {}
        self._pieces = {} # May not be needed for a game but can be ignored


    @property
    def pieces(self):
        return self._pieces

    @abstractmethod
    def print_board(self):
        pass

    def g_deepcopy(self, ais):
        game = deepcopy(self)
        del game._ais
        game._ais = ais
        return game

    @property
    def ais(self):
        return self._ais

    @property
    def board(self):
        return self._board

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

    @abstractmethod
    def start_game(self):
        pass

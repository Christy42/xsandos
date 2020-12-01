from abc import abstractmethod


class Game:
    def __init__(self):
        # Some games may not have a board but that can be changed later
        self._board = []
        self._player_1_ai = None
        self._player_2_ai = None

    @abstractmethod
    def print_board(self):
        pass

    @property
    def board(self):
        return self._board

    @abstractmethod
    def possible_moves(self, **kwargs):
        pass

    # TODO: kwargs abused a bit in subclasses I feel
    @abstractmethod
    def check_end_game(self, **kwargs):
        pass

    @abstractmethod
    def make_move(self, **kwargs):
        pass

    @abstractmethod
    def check_move(self, move):
        pass

    @abstractmethod
    def start_game(self):
        pass

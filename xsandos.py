import numpy as np
from enum import Enum
from copy import deepcopy

from game import Game, GameRunner


class Result(Enum):
    Xs = 1
    Os = 2
    DRAW = 3


class MoveXs(Enum):
    SIDE = 1
    ROW = 2
    COLUMN = 3


# TODO: Square/Colour can be cleaned up and some of the functionality used can be moved to super class
class Square(Enum):
    BLANK = 1
    Xs = 2
    Os = 3

    @property
    def other_side(self):
        return Square.Xs if self.value == Square.Os else Square.Os

    @property
    def side_to_result(self):
        return Result.Xs if self.value == Square.Xs else Square.Os


class XsAndOs(Game):
    def __init__(self):
        super().__init__()
        self._board = [[Square.BLANK, Square.BLANK, Square.BLANK],
                       [Square.BLANK, Square.BLANK, Square.BLANK],
                       [Square.BLANK, Square.BLANK, Square.BLANK]]
        self._next_player = Square.Xs
        self.game_history = []
        self.add_state_to_game_history()

    def check_end_game(self):
        for i in range(3):
            if self._board[i][0] == self._board[i][1] == self._board[i][2] and self._board[i][0] != Square.BLANK:
                return self._board[i][0]
            if self._board[0][i] == self._board[1][i] == self._board[2][i] and self._board[0][i] != Square.BLANK:
                return self._board[0][i]
        if ((self._board[0][0] == self._board[1][1] == self._board[2][2]) or
                (self._board[0][2] == self._board[1][1] == self._board[2][0])) and self._board[1][1] != Square.BLANK:
            return self._board[1][1]
        return False

    def make_move(self, move):
        self._board[move[MoveXs.ROW]][move[MoveXs.COLUMN]] = move[MoveXs.SIDE]
        self._next_player = self.next_player.other_side

    def check_move(self, move):
        return self._board[move[MoveXs.ROW]][move[MoveXs.COLUMN]] == Square.BLANK

    def copy(self, include_history=True):
        game_copy = XsAndOs()
        for i in range(len(game_copy._board)):
            game_copy._board[i] = self._board[i][:]
        game_copy._next_player = self._next_player
        game_copy.game_history = []
        if include_history:
            game_copy.game_history = deepcopy(self.game_history)
        return game_copy

    # TODO: If sides get normalised these could be in the super class
    @staticmethod
    def other_side(side):
        return Square.Os if side == Square.Xs else Square.Xs

    @staticmethod
    def side_to_result(side):
        return Result.Os if side == Square.Os else Result.Xs

    def possible_moves(self, side: Square, ind_piece=None):
        possible_moves = []
        for i in range(len(self._board)):
            for j in range(len(self._board)):
                if self._board[i][j] == Square.BLANK:
                    possible_moves.append({MoveXs.SIDE: self._next_player, MoveXs.ROW: i, MoveXs.COLUMN: j})
        return possible_moves

    def print_board(self):
        print('-'*12)
        for i in range(3):
            line = ""
            for j in range(3):
                square = ' '
                if self._board[i][j] == Square.Xs:
                    square = 'X'
                elif self._board[i][j] == Square.Os:
                    square = 'O'
                line += square
            print(line)
        print('-'*12)

    def add_state_to_game_history(self):
        board_list = []
        for i in range(3):
            for j in range(3):
                position_char = ' '
                if self._board[i][j] == Square.Xs:
                    position_char = 'X'
                elif self._board[i][j] == Square.Os:
                    position_char = 'O'
                board_list.append(position_char)
        board_string = ''.join(board_list)
        self.game_history.append(board_string)


class XsAndOsRunner(GameRunner):
    def __init__(self, X_AIClass=None, O_AIClass=None):
        super().__init__()
        self._game = XsAndOs()
        self._ais = {
            Square.Xs: X_AIClass(self._game, Square.Xs, Square.Os),
            Square.Os: O_AIClass(self._game, Square.Os, Square.Xs),
        }

    def start_game(self, verbose=False):
        if verbose:
            print('New game')
        for i in range(9):
            if verbose:
                self._game.print_board()
            valid_move = False
            move = None
            while not valid_move:
                print(self._game.next_player)
                move = self._ais[self._game.next_player].move()
                valid_move = True if self._game.check_move(move) else False
                if not valid_move:
                    self._game.print_board()
                    assert 0
            self._game.make_move(move)

            game_over = self._game.check_end_game()
            if game_over:
                print(str(game_over).replace("Squares.", "").replace("s", "") + " Win")
                self._ais[game_over].win()
                self._ais[game_over.other_side].loss()
                if verbose:
                    self._game.print_board()
                return game_over.side_to_result
        print("Draw")
        self._ais[Square.Xs].draw()
        self._ais[Square.Os].draw()
        if verbose:
            self._game.print_board()
        return Result.DRAW

    def game_history(self):
        return self._game.game_history


class BruteForceAI:
    def __init__(self, game: XsAndOs, side: Square):
        self._game = game
        self._side = side
        
    def move(self):
        for i in range(3):
            for j in range(3):
                if self._game.board[i][j] == Square.BLANK:
                    return [self._side, i, j]

    def win(self):
        pass

    def draw(self):
        pass

    def loss(self):
        pass
    
                
class NewellSimonAI:
    def __init__(self, game: XsAndOs, side: Square, other_side: Square):
        self._game = game
        self._side = side
        self._board = np.zeros((3, 3))

    def move(self):
        '''Make a move according to the Newell-Simon programme'''
        self._board_as_array()

        for block in [False, True]:
            position = self.win_or_block(block=block)
            if position:
                return {MoveXs.SIDE: self._side, MoveXs.ROW: position[0], MoveXs.COLUMN: position[1]}

        position = self.fork()
        if position:
            return {MoveXs.SIDE: self._side, MoveXs.ROW: position[0], MoveXs.COLUMN: position[1]}

        position = self.block_fork()
        if position:
            return {MoveXs.SIDE: self._side, MoveXs.ROW: position[0], MoveXs.COLUMN: position[1]}

        position = self.empty_square()
        if position:
            return {MoveXs.SIDE: self._side, MoveXs.ROW: position[0], MoveXs.COLUMN: position[1]}

        self._game.print_board()
        raise RuntimeError("No valid moves. Is the board full?")
        
    def win_or_block(self, block: bool):
        '''Find and play/block any available winning moves.'''
        target = (-2 if block else 2)
        for i in range(3):
            if self._board[i, :].sum() == target:
                return i, np.where(self._board[i, :] == 0)[0][0]
            if self._board[:, i].sum() == target:
                return np.where(self._board[:, i] == 0)[0][0], i
        if np.diag(self._board).sum() == target:
            i = np.where(np.diag(self._board) == 0)[0][0]
            return i, i
        if np.diag(np.fliplr(self._board)).sum() == target:
            i = np.where(np.diag(np.fliplr(self._board)) == 0)[0][0]
            return i, 2-i

    def fork(self):
        '''Find and play any available 2-way forks.'''
        for i in range(3):
            for j in range(3):
                possible_board = self._board.copy()
                if possible_board[i, j] != 0:
                    continue
                possible_board[i, j] = 1
                if self._has_fork(possible_board, block=False):
                    return i, j

    def block_fork(self):
        '''Look for and block opponent forks.'''
        forks = []
        for i in range(3):
            for j in range(3):
                possible_board = self._board.copy()
                if possible_board[i, j] != 0:
                    continue
                possible_board[i, j] = -1
                if self._has_fork(possible_board, block=True):
                    forks.append((i, j))
        if len(forks) == 1:
            return forks[0]
        if len(forks) == 0:
            return None

        # If there is more than 1 fork, we have to be careful:
        # we must threaten a 3-in-a-row, but only somewhere
        # that they cannot create a fork.
        possible_board = self._board.copy()
        for fork in forks:
            possible_board[fork] = 10000
        for i in range(3):
            for j in range(3):
                if possible_board[i, j] != 0:
                    continue
                possible_board[i, j] = 1
                if possible_board[:, i].sum() == 2 or possible_board[i, :].sum() == 2:
                    return i, j
                if np.diag(possible_board).sum() == 2 or np.diag(np.fliplr(possible_board)).sum() == 2:
                    return i, j
                possible_board[i, j] = 0

    def empty_square(self):
        '''No wins or forks to play/block, so play an advantageous square.'''
        # First the middle
        if self._board[1, 1] == 0:
            return 1, 1
        # Next opposite corners
        for corner in ((0, 0), (0, 2), (2, 0), (2, 2)):
            if self._board[corner] == -1:
                opposite = (2-corner[0], 2-corner[1])
                if self._board[opposite] == 0:
                    return opposite
        # Now any available corner
        for corner in ((0, 0), (0, 2), (2, 0), (2, 2)):
            if self._board[corner] == 0:
                return corner
        # Finally any available square:
        for square in ((1, 0), (1, 2), (0, 1), (2, 1)):
            if self._board[square] == 0:
                return square

    def _has_fork(self, board, block: bool):
        '''A fork is any situation where there are >= 2 winning opportunities. So count the available wins.'''
        target = (-2 if block else 2)
        count = int(np.diag(board).sum() == target) + int(np.diag(np.fliplr(board)).sum() == target)
        for i in range(3):
            count += int(board[i, :].sum() == target) + int(board[:, i].sum() == target)
        return (count >= 2)

    def _board_as_array(self):
        '''Store game board as np array for easier slicing.'''
        for i in range(3):
            for j in range(3):
                if self._game.board[i][j] == self._side:
                    self._board[i, j] = 1
                elif self._game.board[i][j] != Square.BLANK:
                    self._board[i, j] = -1

    def win(self):
        pass

    def draw(self):
        pass

    def loss(self):
        pass

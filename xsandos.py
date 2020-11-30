import numpy as np
import random
from enum import Enum


class Result(Enum):
    Xs = 1
    Os = 2
    DRAW = 3

    
class Square(Enum):
    BLANK = 1
    Xs = 2
    Os = 3


class Side(Enum):
    Xs = 1
    Os = 2


class Game:
    def __init__(self, X_AIClass, O_AIClass):
        self._x_ai = X_AIClass(self, Side.Xs)
        self._o_ai = O_AIClass(self, Side.Os)
        self._squares = [[Square.BLANK, Square.BLANK, Square.BLANK],
                         [Square.BLANK, Square.BLANK, Square.BLANK],
                         [Square.BLANK, Square.BLANK, Square.BLANK]]

    @property
    def squares(self):
        return self._squares

    def check_win(self):
        for i in range(3):
            if self._squares[i][0] == self._squares[i][1] == self._squares[i][2]:
                return self._squares[i][0]
        for i in range(3):
            if self._squares[0][i] == self._squares[1][i] == self._squares[2][i]:
                return self._squares[0][i]
        if self._squares[0][0] == self._squares[1][1] == self._squares[2][2]:
            return self._squares[1][1]
        if self._squares[0][2] == self._squares[1][1] == self._squares[2][0]:
            return self._squares[1][1]
        return False

    def start_game(self, verbose=False):
        if verbose:
            print('New game')
        xs_turn = True
        for i in range(9):
            if verbose:
                self.print_board()
            valid_move = False
            row, col = 0, 0
            while not valid_move:
                if xs_turn:
                    row, col = self._x_ai.move()
                else:
                    row, col = self._o_ai.move()
                valid_move = True if self._squares[row][col] == Square.BLANK else False
                if not valid_move:
                    self.print_board()
                    print((row,col))
                    assert 0
            self._squares[row][col] = Square.Xs if xs_turn else Square.Os
            xs_turn = not xs_turn
            game_over = self.check_win()
            if game_over == Square.Xs:
                print("X Win")
                self._x_ai.win()
                self._o_ai.loss()
                if verbose:
                    self.print_board()
                return Result.Xs
            if game_over == Square.Os:
                print("O Win")
                self._x_ai.loss()
                self._o_ai.win()
                if verbose:
                    self.print_board()
                return Result.Os
        print("Draw")
        self._x_ai.draw()
        self._o_ai.draw()
        if verbose:
            self.print_board()
        return Result.DRAW

    def possible_moves(self, side: Side, ind_piece=None):
        possible_moves = []
        for i in range(len(self._squares)):
            for j in range(len(self._squares)):
                if self._squares[i][j] == Square.BLANK:
                    possible_moves.append([i, j])
        return possible_moves

    def print_board(self):
        print('-'*12)
        for i in range(3):
            line = ""
            for j in range(3):
                square = ' '
                if self._squares[i][j] == Square.Xs:
                    square = 'X'
                elif self._squares[i][j] == Square.Os:
                    square = 'O'
                line += square
            print(line)
        print('-'*12)


class BruteForceAI:
    def __init__(self, game: Game, side: Side):
        self._game = game
        self._side = side
        
    def move(self):
        for i in range(3):
            for j in range(3):
                if self._game.squares[i][j] == Square.BLANK:
                    return i, j

    def win(self):
        pass

    def draw(self):
        pass

    def loss(self):
        pass

    
class RandomAI:
    def __init__(self, game: Game, side: Side):
        self._game = game
        self._side = side
        self._my_square = (Square.Xs if self._side == Side.Xs else Square.Os)
        self._board = np.zeros((3,3), dtype='int')

    def move(self):
        return random.choice(self._game.possible_moves(self._side))

    def win(self):
        pass

    def draw(self):
        pass

    def loss(self):
        pass
    
                
class NewellSimonAI:
    def __init__(self, game: Game, side: Side):
        self._game = game
        self._side = side
        self._my_square = (Square.Xs if self._side == Side.Xs else Square.Os)
        self._board = np.zeros((3,3))

    def move(self):
        '''Make a move according to the Newell-Simon programme'''
        self._board_as_array()

        for block in [False, True]:
            position = self.win_or_block(block=block)
            if position:
                return position

        position = self.fork()
        if position:
            return position

        position = self.block_fork()
        if position:
            return position

        position = self.empty_square()
        if position:
            return position

        self._game.print_board()
        raise RuntimeError("No valid moves. Is the board full?")
        
    def win_or_block(self, block: bool):
        '''Find and play/block any available winning moves.'''
        target = (-2 if block else 2)
        for i in range(3):
            if self._board[i,:].sum() == target:
                return i, np.where(self._board[i,:]==0)[0][0]
            if self._board[:,i].sum() == target:
                return np.where(self._board[:,i]==0)[0][0], i
        if np.diag(self._board).sum() == target:
            i = np.where(np.diag(self._board)==0)[0][0]
            return i,i
        if np.diag(np.fliplr(self._board)).sum() == target:
            i = np.where(np.diag(np.fliplr(self._board))==0)[0][0]
            return i,2-i

    def fork(self):
        '''Find and play any available 2-way forks.'''
        for i in range(3):
            for j in range(3):
                possible_board = self._board.copy()
                if possible_board[i,j] != 0:
                    continue
                possible_board[i,j] = 1
                if self._has_fork(possible_board, block=False):
                    return i,j

    def block_fork(self):
        '''Look for and block opponent forks.'''
        forks = []
        for i in range(3):
            for j in range(3):
                possible_board = self._board.copy()
                if possible_board[i,j] != 0:
                    continue
                possible_board[i,j] = -1
                if self._has_fork(possible_board, block=True):
                    forks.append((i,j))
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
                if possible_board[i,j] != 0:
                    continue
                possible_board[i,j] = 1
                if possible_board[:,i].sum() == 2 or possible_board[i,:].sum() == 2:
                    return i,j
                if np.diag(possible_board).sum() == 2 or np.diag(np.fliplr(possible_board)).sum() == 2:
                    return i,j
                possible_board[i,j] = 0

    def empty_square(self):
        '''No wins or forks to play/block, so play an advantageous square.'''
        # First the middle
        if self._board[1,1] == 0:
            return 1,1
        # Next opposite corners
        for corner in ((0,0), (0,2), (2,0), (2,2)):
            if self._board[corner] == -1:
                opposite = (2-corner[0], 2-corner[1])
                if self._board[opposite] == 0:
                    return opposite
        # Now any available corner
        for corner in ((0,0), (0,2), (2,0), (2,2)):
            if self._board[corner] == 0:
                return corner
        # Finally any available square:
        for square in ((1,0), (1,2), (0,1), (2,1)):
            if self._board[square] == 0:
                return square

    def _has_fork(self, board, block: bool):
        '''A fork is any situation where there are >= 2 winning oportunities. So count the available wins.'''
        target = (-2 if block else 2)
        count = int(np.diag(board).sum() == target) + int(np.diag(np.fliplr(board)).sum() == target)
        for i in range(3):
            count += int(board[i,:].sum() == target) + int(board[:,i].sum() == target)
        return (count >= 2)

    def _board_as_array(self):
        '''Store game board as np array for easier slicing.'''
        for i in range(3):
            for j in range(3):
                if self._game.squares[i][j] == self._my_square:
                    self._board[i,j] = 1
                elif self._game.squares[i][j] != Square.BLANK:
                    self._board[i,j] = -1

    def win(self):
        pass

    def draw(self):
        pass

    def loss(self):
        pass
                    

class StateLearnerAI:
    
    states_seen  = {}
    states_won   = {}
    states_drawn = {}
    states_lost  = {}

    def __init__(self, game: Game, side: Side):
        self._game = game
        self._side = side
        self._my_square = (Square.Xs if self._side == Side.Xs else Square.Os)
        self._board = np.zeros((3,3), dtype='int')
        self.this_game_states = []

    def move(self):
        board_tuple = self.get_board_tuple()
        move = self.get_best_historical_move(board_tuple)
        board_list = list(board_tuple)
        board_list[move[0]*3 + move[1]] = 'M'
        self.this_game_states.append(tuple(board_list))
        return move

    def get_position_rating(self, board_tuple):
        if board_tuple not in self.states_seen:
            return 0
        num_times_seen  = self.states_seen[board_tuple]
        num_times_won   = self.states_won[board_tuple]
        num_times_drawn = self.states_drawn[board_tuple]
        num_times_lost  = self.states_lost[board_tuple]

        return (num_times_won * 3. + num_times_drawn - 200*num_times_lost) / num_times_seen

    def get_best_historical_move(self, board_tuple):
        best_pos = None
        best_ranking = None
        board_list = list(board_tuple)
        for pos in range(9):
            if board_list[pos] != ' ':
                continue
            board_list[pos] = 'M'
            pos_ranking = self.get_position_rating(tuple(board_list))
            board_list[pos] = ' '
            if best_ranking is None or pos_ranking > best_ranking:
                best_pos = pos
                best_ranking = pos_ranking
        return best_pos // 3, best_pos % 3

    def get_board_tuple(self):
        board_list = []
        for i in range(3):
            for j in range(3):
                square = ' '
                if self._game.squares[i][j] == self._my_square:
                    square = 'M'  # my square
                elif self._game.squares[i][j] != Square.BLANK:
                    square = 'E'  # enemy square
                board_list.append(square)
        return tuple(board_list)

    def win(self):
        self.update_num_seen()
        for state in self.this_game_states:
            self.states_won[state] += 1

    def draw(self):
        self.update_num_seen()
        for state in self.this_game_states:
            self.states_drawn[state] += 1

    def loss(self):
        self.update_num_seen()
        for state in self.this_game_states:
            #print('Recording: {}'.format(state))
            self.states_lost[state] += 1

    def update_num_seen(self):
        for state in self.this_game_states:
            if state not in self.states_seen:
                self.states_seen[state]  = 1
                self.states_won[state]   = 0
                self.states_drawn[state] = 0
                self.states_lost[state] = 0
        

print('X - NewellSimonAI; O - StateLearnerAI')
for i in range(50):
    b = Game(NewellSimonAI, StateLearnerAI)
    b.start_game(verbose=False)

print('\n\nX - StateLearnerAI; O - NewellSimonAI')
for i in range(30):
    b = Game(StateLearnerAI, NewellSimonAI)
    b.start_game(verbose=False)

print('\n\nX - StateLearnerAI; O - StateLearnerAI')
for i in range(30):
    b = Game(StateLearnerAI, StateLearnerAI)
    b.start_game(verbose=False)

print('\n\nX - RandomAI; O - StateLearnerAI')
for i in range(1):
    b = Game(RandomAI, RandomAI)
    b.start_game(verbose=True)

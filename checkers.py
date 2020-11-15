import numpy as np
from enum import Enum
import random
import math


def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)


def sum_l(lister):
    ans = ''
    for element in lister:
        ans = ans + ', ' + element
    return ans[2:]


class Result(Enum):
    WHITE = 1
    BLACK = 2
    DRAW = 3


class MoveType(Enum):
    MOVE = 1
    JUMP = 2


class Colour(Enum):
    BLANK = 1
    WHITE = 2
    BLACK = 3


class Direction(Enum):
    UP_RIGHT = 1  # [-1, 1]
    UP_LEFT = 2   # [-1, -1]
    DOWN_RIGHT = 3  # [1, 1]
    DOWN_LEFT = 4  # [1, -1]


class Piece:
    def __init__(self, colour: Colour, position: list):
        self._colour = colour
        self._position = position
        # Just kept for learning purposes
        self._king = False
        self._direction = [Direction.UP_RIGHT, Direction.UP_LEFT] if colour == Colour.BLACK else \
            [Direction.DOWN_RIGHT, Direction.DOWN_LEFT]

    @property
    def colour(self):
        return self._colour

    def move(self, direction: Direction):
        self._position = Checkers.adj_square(self._position, direction)

    @property
    def other_colour(self):
        return Colour.BLACK if self._colour == Colour.WHITE else Colour.WHITE

    @property
    def position(self):
        return self._position

    @property
    def direction(self):
        return self._direction

    @property
    def king(self):
        return self._king

    def king_piece(self):
        self._direction = [Direction.UP_RIGHT, Direction.UP_LEFT, Direction.DOWN_RIGHT, Direction.DOWN_LEFT]
        self._king = True

    def remove_piece(self):
        self._position = [-1, -1]


class Checkers:
    def __init__(self, Black_AIClass=None, White_AIClass=None, board=None):
        if board:
            self._board = [[board[i] for i in range(j, j+8)] for j in [8 * k for k in range(8)]]
        else:
            self._board = [[Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE],
                           [Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK],
                           [Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE],
                           [Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK],
                           [Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK],
                           [Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK],
                           [Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK],
                           [Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK]]
        self._turn_count = 0
        self.turns_since_last_piece_taken = 0
        if Black_AIClass:
            self._black_ai = Black_AIClass(self, Colour.BLACK)
        else:
            self._black_ai = None
        if White_AIClass:
            self._white_ai = White_AIClass(self, Colour.WHITE)
        else:
            self._white_ai = None
        self._turn = Colour.BLANK
        # TODO: Can we relate this to the board up above
        self._pieces = {Colour.WHITE: [], Colour.BLACK: []}
        # print(self._board)
        for i in range(8):
            for j in range(8):
                if self._board[i][j] != Colour.BLANK:
                    self._pieces[self._board[i][j]].append(Piece(self._board[i][j], [i, j]))

    @property
    def pieces(self):
        return self._pieces

    @property
    def board(self):
        return self._board

    def check_move(self, piece: Piece, direction: Direction):
        # TODO: Include an input in case an individual piece is required to move
        # TODO: Double check that the right colour is being picked
        # Piece already taken
        if piece.position == [-1, -1]:
            return False, None
        # Piece moving backwards illegally
        if direction not in piece.direction:
            return False, None
        new_square = self.adj_square(piece.position, direction)
        # new square off the board
        if min(new_square) < 0 or max(new_square) > 7:
            return False, None
        # Can't move through square with own piece
        if self._board[new_square[0]][new_square[1]] == piece.colour:
            return False, None
        # Other colour, potential jump
        if self._board[new_square[0]][new_square[1]] == piece.other_colour:
            jump_square = self.adj_square(new_square, direction)
            # can't jump off the board
            if min(jump_square) < 0 or max(jump_square) > 7:
                return False, None
            # Can't jump onto square with any piece
            if self._board[jump_square[0]][jump_square[1]] != Colour.BLANK:
                return False, None
            return True, MoveType.JUMP
        # Player must make a jump if required
        if self.check_jump_required(piece.colour):
            return False, None
        return True, MoveType.MOVE

    def make_move(self, piece: Piece, direction: Direction):
        allowed, m_type = self.check_move(piece, direction)
        if allowed:
            if m_type == MoveType.MOVE:
                self.turns_since_last_piece_taken += 1
                self._board[piece.position[0]][piece.position[1]] = Colour.BLANK
                piece.move(direction)
                self._board[piece.position[0]][piece.position[1]] = piece.colour
                if piece.position[0] in [0, 7]:
                    piece.king_piece()
                return True
            if m_type == MoveType.JUMP:
                self.turns_since_last_piece_taken = 0
                new_square = self.adj_square(piece.position, direction)
                self._board[piece.position[0]][piece.position[1]] = Colour.BLANK
                self._board[new_square[0]][new_square[1]] = Colour.BLANK

                for piece_taken in self._pieces[piece.other_colour]:
                    if piece_taken.position == new_square:
                        piece_taken.remove_piece()
                piece.move(direction)
                piece.move(direction)
                self._board[piece.position[0]][piece.position[1]] = piece.colour
                # OK, bad abstraction here.  Should only be a king if in the last,
                # This is first and last how the only way to move to the first row is if already a king
                # making the same piece a king repeatedly has no effect. should be cleaner
                if piece.position[0] in [0, 7]:
                    piece.king_piece()
                # TODO: Can a piece jump to the last line and immediately jump backwards???
                if self.check_piece_can_take(piece):
                    valid_move = False
                    while not valid_move:
                        if piece.colour == Colour.BLACK:
                            piece, direction = self._black_ai.move(must_jump=True, ind_piece=piece)
                        else:
                            piece, direction = self._white_ai.move(must_jump=True, ind_piece=piece)
                        valid_move = self.check_move(piece, direction)
                    self.make_move(piece, direction)

                if self.check_piece_can_take(piece):
                    pass
                return True
        return False

    def check_piece_can_take(self, piece: Piece):
        # Check 4 directions
        for element in Direction:
            if element not in piece.direction:
                # Can't take in the wrong direction
                continue
            new_square = self.adj_square(piece.position, element)
            jump_square = self.adj_square(new_square, element)
            # Check these squares are on the board
            if min(jump_square) < 0 or max(jump_square) > 7:
                continue
            if (self._board[new_square[0]][new_square[1]] == piece.other_colour and
               self._board[jump_square[0]][jump_square[1]] == Colour.BLANK):
                return True
        return False

    def check_jump_required(self, colour: Colour):
        for piece in self._pieces[colour]:
            if self.check_piece_can_take(piece):
                return True
        return False

    @staticmethod
    def adj_square(place: list, direc: Direction):
        return [sum(x) for x in zip(place, [-1, 1] if direc == Direction.UP_RIGHT else
                [-1, -1] if direc == Direction.UP_LEFT else
                [1, 1] if direc == Direction.DOWN_RIGHT else [1, -1])]

    def check_game_lost(self, colour: Colour):
        if self._turn_count > 15:
            white_pieces = [piece for piece in self._pieces[Colour.WHITE] if piece.position[0] >= 0]
            black_pieces = [piece for piece in self._pieces[Colour.BLACK] if piece.position[0] >= 0]
            if len(white_pieces) > len(black_pieces):
                return Result.WHITE
            if len(black_pieces) > len(white_pieces):
                return Result.BLACK
            return Result.DRAW
        if self.turns_since_last_piece_taken >= 100:
            return Result.DRAW
        for piece in self._pieces[colour]:
            # The dead don't move
            if piece.position[0] < 0:
                continue
            if self.check_piece_can_take(piece):
                return False
            for direction in Direction:
                new_square = self.adj_square(piece.position, direction)
                if min(new_square) < 0 or max(new_square) > 7:
                    continue
                if direction not in piece.direction:
                    continue
                if self._board[new_square[0]][new_square[1]] == Colour.BLANK:
                    return False
        return Result.WHITE if colour == Colour.BLACK else Result.BLACK

    def start_game(self, verbose=False):
        self._turn = Colour.BLACK
        while True:
            self._turn_count += 1
            valid_move = False
            piece = self._pieces[Colour.WHITE][0]
            direction = Direction.DOWN_LEFT
            while not valid_move:
                if self._turn == Colour.BLACK:
                    piece, direction = self._black_ai.move(must_jump=self.check_jump_required(Colour.BLACK),
                                                           ind_piece=None)
                else:
                    piece, direction = self._white_ai.move(must_jump=self.check_jump_required(Colour.WHITE),
                                                           ind_piece=None)

                valid_move, style = self.check_move(piece, direction)
            self.make_move(piece, direction)
            if verbose or self._turn_count > 1000:
                print("")
                print("")
                print("XXXXX")
                print(self._turn_count)
                print(self.turns_since_last_piece_taken)
                for i in range(8):
                    new_row = [colored(255 if self._board[i][j] != Colour.WHITE else 0, 255 if self._board[i][j] != Colour.BLACK else 0, 255 if self._board[i][j]==Colour.BLANK else 0, str(self._board[i][j])) for j in range(8)]
                    print(sum_l(new_row))
            self._turn = Colour.WHITE if self._turn == Colour.BLACK else Colour.BLACK
            game_over = self.check_game_lost(self._turn)
            if game_over == Result.WHITE:
                if verbose:
                    print("White Win")
                self._black_ai.loss()
                self._white_ai.win()
                return Result.WHITE
            if game_over == Result.BLACK:
                if verbose:
                    print("Black Win")
                self._black_ai.win()
                self._white_ai.loss()
                return Result.BLACK
            if game_over == Result.DRAW:
                if verbose:
                    print("Draw")
                self._black_ai.draw()
                self._white_ai.draw()
                return Result.DRAW


class RandomAI:
    def __init__(self, game: Checkers, colour: Colour):
        self._game = game
        self._colour = colour

    def win(self):
        pass

    def loss(self):
        pass

    def draw(self):
        pass

    def move(self, must_jump=False, ind_piece=None):
        pot_pieces = {}
        if ind_piece:
            pot_pieces = {ind_piece: []}
            for direction in Direction:
                value, style = self._game.check_move(ind_piece, direction)
                # should always be a jump required if a piece is mandated to be used but for completeness
                if not must_jump and value:
                    pot_pieces[ind_piece].append(direction)
                elif must_jump and style == MoveType.JUMP:
                    pot_pieces[ind_piece].append(direction)
        elif must_jump:
            for piece in self._game.pieces[self._colour]:
                if piece.position == [-1, -1]:
                    continue
                if self._game.check_piece_can_take(piece):
                    pot_pieces.update({piece: []})

                for poss in pot_pieces:
                    for direction in Direction:
                        value, style = self._game.check_move(poss, direction)
                        if style == MoveType.JUMP:
                            pot_pieces[poss].append(direction)
        else:
            for piece in self._game.pieces[self._colour]:
                if piece.position == [-1, -1]:
                    continue
                for direction in Direction:
                    value, style = self._game.check_move(piece, direction)
                    if value:
                        if piece not in pot_pieces:
                            pot_pieces[piece] = [direction]
                        else:
                            pot_pieces[piece].append([direction])
        if len(pot_pieces) == 0:
            raise Exception("No valid move found")
        piece = random.choice(list(pot_pieces.keys()))
        direction = random.choice(pot_pieces[piece])
        # input("Press Enter to continue...")

        return piece, direction


class StateLearnerAI:
    states_seen = {}
    states_won = {}
    states_drawn = {}
    states_lost = {}
    total_wins = 0
    total_draws = 0
    total_losses = 0

    def __init__(self, game: Checkers, side: Colour):
        self._game = game
        self._side = side
        self._other_side = Colour.WHITE if side == Colour.BLACK else Colour.BLACK
        self._board = np.zeros((8, 8), dtype='int')
        self.this_game_states = []

    def move(self, must_jump=False, ind_piece=None):
        board_tuple = self.get_board_tuple(self._game.board)
        piece, direction, new_board = self.get_best_historical_move(board_tuple, ind_piece)
        self.this_game_states.append(self.get_board_tuple(new_board))
        return piece, direction

    def get_position_rating(self, board_tuple):
        if board_tuple not in self.states_seen:
            return 0
        num_times_seen = self.states_seen[board_tuple]
        num_times_won = self.states_won[board_tuple]
        num_times_drawn = self.states_drawn[board_tuple]
        num_times_lost = self.states_lost[board_tuple]
        return (num_times_won * 3. + num_times_drawn - 200 * num_times_lost) / num_times_seen

    def get_best_historical_move(self, board_tuple, ind_piece=None):
        best_piece = None
        best_direction = None
        best_ranking = None
        new_board = None
        board_list = list(board_tuple)
        # TODO: Get a list of all possible moves and try them on a separate board
        for piece in self._game.pieces[self._side]:
            if piece.position[0] < 0:
                continue
            if ind_piece:
                if piece.position != ind_piece.position:
                    continue
            for direction in Direction:
                if not self._game.check_move(piece, direction)[0]:
                    continue
                # print(self._game.check_move(piece, direction))
                # TODO: Need to put colours back in board state
                board_set = self.board_set(board_list)
                # Note that the randomAI will only take effect if multiple jumps are made in a single turn
                # This is not great but not terrible as the odds of this being have multiple choices are slim
                game_check = Checkers(RandomAI, RandomAI, board=board_set)
                rel_piece = None
                for element in game_check.pieces[self._side]:
                    if element.position == piece.position:
                        rel_piece = element
                # TODO: Need to alter the new board state to suit the board

                game_check.make_move(rel_piece, direction)
                new_board_tuple = self.get_board_tuple(game_check.board)
                pos_ranking = self.get_position_rating(new_board_tuple)
                # print(-pos_ranking / (2 * max(best_ranking, 0.01)))
                ranked = best_ranking if best_ranking else 0.1
                # print(min(max(-pos_ranking / (2 * ranked), -100), 100))
                if best_ranking is None or random.random() < math.exp(min(max(-pos_ranking / (2 * ranked), -100), 100)):
                    best_piece = piece
                    best_direction = direction
                    best_ranking = pos_ranking
                    new_board = game_check.board
        return best_piece, best_direction, new_board

    def board_set(self, board):
        return [Colour.BLANK if board[i] == ' ' else self._side if board[i] == 'M' else self._other_side for i in range(64)]

    def get_board_tuple(self, board):
        board_list = []
        for i in range(8):
            for j in range(8):
                square = ' '
                if board[i][j] == self._side:
                    square = 'M'  # my square
                elif board[i][j] != Colour.BLANK:
                    square = 'E'  # enemy square
                board_list.append(square)
        return tuple(board_list)

    def win(self):
        self.update_num_seen()
        self.total_wins += 1
        for state in self.this_game_states:
            self.states_won[state] += 1

    def draw(self):
        self.total_draws += 1
        self.update_num_seen()
        for state in self.this_game_states:
            self.states_drawn[state] += 1

    def loss(self):
        self.total_losses += 1
        self.update_num_seen()
        for state in self.this_game_states:
            # print('Recording: {}'.format(state))
            self.states_lost[state] += 1

    def update_num_seen(self):
        for state in self.this_game_states:
            if state not in self.states_seen:
                self.states_seen[state] = 1
                self.states_won[state] = 0
                self.states_drawn[state] = 0
                self.states_lost[state] = 0


checkers = Checkers(Black_AIClass=RandomAI, White_AIClass=StateLearnerAI)
checkers.start_game(verbose=True)
print('\n\nX - RandomAI; O - StateLearnerAI')
wins = 0
losses = 0
draws = 0
for i in range(100000):
    if i % 10 == 0:
        print("YYY")
        print(i)
        print(wins)
        print(draws)
        print(losses)
    b = Checkers(Black_AIClass=RandomAI, White_AIClass=StateLearnerAI)
    win = b.start_game(verbose=False)
    if win == Result.BLACK:
        wins += 1
    elif win == Result.WHITE:
        losses += 1
    else:
        draws += 1

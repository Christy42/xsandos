import numpy as np
from enum import Enum
import random


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
    def __init__(self, Black_AIClass, White_AIClass):
        self._board = [[Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE],
                       [Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK],
                       [Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE],
                       [Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK],
                       [Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK],
                       [Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK],
                       [Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK],
                       [Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK]]
        self.turns_since_last_piece_taken = 0
        self._black_ai = Black_AIClass(self, Colour.BLACK)
        self._white_ai = White_AIClass(self, Colour.WHITE)
        self._pieces = {Colour.WHITE:
                            [Piece(Colour.WHITE, [0, 1]), Piece(Colour.WHITE, [0, 3]), Piece(Colour.WHITE, [0, 5]),
                             Piece(Colour.WHITE, [0, 7]), Piece(Colour.WHITE, [1, 0]), Piece(Colour.WHITE, [1, 2]),
                             Piece(Colour.WHITE, [1, 4]), Piece(Colour.WHITE, [1, 6]), Piece(Colour.WHITE, [2, 1]),
                             Piece(Colour.WHITE, [2, 3]), Piece(Colour.WHITE, [2, 5]), Piece(Colour.WHITE, [2, 7])],
                        Colour.BLACK:
                            [Piece(Colour.BLACK, [7, 0]), Piece(Colour.BLACK, [7, 2]), Piece(Colour.BLACK, [7, 4]),
                             Piece(Colour.BLACK, [7, 6]), Piece(Colour.BLACK, [6, 1]), Piece(Colour.BLACK, [6, 3]),
                             Piece(Colour.BLACK, [6, 5]), Piece(Colour.BLACK, [6, 7]), Piece(Colour.BLACK, [5, 0]),
                             Piece(Colour.BLACK, [5, 2]), Piece(Colour.BLACK, [5, 4]), Piece(Colour.BLACK, [5, 6])]
                        }

    @property
    def pieces(self):
        return self._pieces

    @property
    def board(self):
        return self._board

    def check_move(self, piece: Piece, direction: Direction):
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
        if self.turns_since_last_piece_taken >= 100:
            return Result.DRAW
        return Result.WHITE if colour == Colour.BLACK else Result.BLACK

    def start_game(self, verbose=False):
        blacks_turn = True
        turn = 0
        while True:
            turn += 1
            valid_move = False
            piece = self._pieces[Colour.WHITE][0]
            direction = Direction.DOWN_LEFT
            while not valid_move:
                if blacks_turn:
                    piece, direction = self._black_ai.move(must_jump=self.check_jump_required(Colour.BLACK),
                                                           ind_piece=None)
                else:
                    piece, direction = self._white_ai.move(must_jump=self.check_jump_required(Colour.WHITE),
                                                           ind_piece=None)

                valid_move, style = self.check_move(piece, direction)
            self.make_move(piece, direction)
            if verbose:
                print("")
                print("")
                print(turn)
                for i in range(8):
                    # print(self._board[i])
                    new_row = [colored(255 if self._board[i][j]!=Colour.WHITE else 0, 255 if self._board[i][j]!=Colour.BLACK else 0, 255 if self._board[i][j]==Colour.BLANK else 0, str(self._board[i][j])) for j in range(8)]
                    print(sum_l(new_row))
            blacks_turn = not blacks_turn
            game_over = self.check_game_lost(Colour.BLACK if blacks_turn else Colour.WHITE)
            if game_over == Result.WHITE:
                if verbose:
                    print("White Win")
                return Result.WHITE
            if game_over == Result.BLACK:
                if verbose:
                    print("Black Win")
                return Result.BLACK
            if game_over == Result.DRAW:
                if verbose:
                    print("Draw")
                return Result.DRAW


class RandomAI:
    def __init__(self, game: Checkers, colour: Colour):
        self._game = game
        self._colour = colour

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

    def __init__(self, game: Checkers, side: Colour):
        self._game = game
        self._side = side
        self._board = np.zeros((8, 8), dtype='int')
        self.this_game_states = []

    def move(self, must_jump=False, ind_piece=False):
        board_tuple = self.get_board_tuple()
        move = self.get_best_historical_move(board_tuple)
        board_list = list(board_tuple)
        board_list[move[0] * 3 + move[1]] = 'M'
        self.this_game_states.append(tuple(board_list))
        return move

    def get_position_rating(self, board_tuple):
        if board_tuple not in self.states_seen:
            return 0
        num_times_seen = self.states_seen[board_tuple]
        num_times_won = self.states_won[board_tuple]
        num_times_drawn = self.states_drawn[board_tuple]
        num_times_lost = self.states_lost[board_tuple]

        return (num_times_won * 3. + num_times_drawn - 200 * num_times_lost) / num_times_seen

    def get_best_historical_move(self, board_tuple):
        best_pos = None
        best_ranking = None
        board_list = list(board_tuple)
        # TODO: Get a list of all possible moves and try them on a separate board
        for pos in range(64):
            if board_list[pos] != ' ':
                continue
            board_list[pos] = 'M'
            pos_ranking = self.get_position_rating(tuple(board_list))
            board_list[pos] = ' '
            if best_ranking is None or pos_ranking > best_ranking:
                best_pos = pos
                best_ranking = pos_ranking
        return best_pos // 8, best_pos % 8

    def get_board_tuple(self):
        board_list = []
        for i in range(8):
            for j in range(8):
                square = ' '
                if self._game.board[i][j] == self._side:
                    square = 'M'  # my square
                elif self._game.board[i][j] != Colour.BLANK:
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
            # print('Recording: {}'.format(state))
            self.states_lost[state] += 1

    def update_num_seen(self):
        for state in self.this_game_states:
            if state not in self.states_seen:
                self.states_seen[state] = 1
                self.states_won[state] = 0
                self.states_drawn[state] = 0
                self.states_lost[state] = 0


checkers = Checkers(StateLearnerAI, RandomAI)
checkers.start_game(verbose=False)

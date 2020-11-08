from enum import Enum


class Colour(Enum):
    BLANK = 1
    WHITE = 2
    BLACK = 3


class Direction(Enum):
    UP = 1
    DOWN = 2


class MoveDirection(Enum):
    UP_RIGHT = 1 # [1, 1]
    UP_LEFT = 2   # [1, -1]
    DOWN_RIGHT = 3 # [-1, 1]
    DOWN_LEFT = 4 # [-1, -1]


class Piece:
    def __init__(self, colour, position):
        self._colour = colour
        self._position = position
        self._king = False
        if colour == Colour.WHITE:
            self._direction = Direction.UP
        else:
            self._direction = Direction.DOWN

    @property
    def colour(self):
        return self._colour

    def move(self, direction: MoveDirection):
        self._position = [sum(x) for x in zip(self._position, [1, 1] if direction == MoveDirection.UP_RIGHT else
        [1, -1] if direction == MoveDirection.UP_LEFT else [-1, 1] if direction == MoveDirection.DOWN_RIGHT else [-1, -1])]

    @property
    def other_colour(self):
        return Colour.BLACK if self._colour == Colour.WHITE else Colour.WHITE

    @property
    def position(self):
        return self._position

    @property
    def king(self):
        return self._king

    def king_piece(self):
        self._king = True

    def remove_piece(self):
        self._position = [-1, -1]


# Needed?
class Board:
    def __init__(self):
        self.state = [[Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE],
                      [Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK],
                      [Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE],
                      [Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK],
                      [Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK],
                      [Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK],
                      [Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK],
                      [Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK]]


class Game:
    def __init__(self):
        self._board = Board()
        self._white = [Piece(Colour.WHITE, [0, 1]), Piece(Colour.WHITE, [0, 3]), Piece(Colour.WHITE, [0, 5]),
                       Piece(Colour.WHITE, [0, 7]), Piece(Colour.WHITE, [1, 0]), Piece(Colour.WHITE, [1, 2]),
                       Piece(Colour.WHITE, [1, 4]), Piece(Colour.WHITE, [1, 6]), Piece(Colour.WHITE, [2, 1]),
                       Piece(Colour.WHITE, [2, 3]), Piece(Colour.WHITE, [2, 5]), Piece(Colour.WHITE, [2, 7])]
        self._black = [Piece(Colour.BLACK, [7, 0]), Piece(Colour.BLACK, [7, 2]), Piece(Colour.BLACK, [7, 4]),
                       Piece(Colour.BLACK, [7, 6]), Piece(Colour.BLACK, [6, 1]), Piece(Colour.BLACK, [6, 3]),
                       Piece(Colour.BLACK, [6, 5]), Piece(Colour.BLACK, [6, 7]), Piece(Colour.BLACK, [5, 0]),
                       Piece(Colour.BLACK, [5, 2]), Piece(Colour.BLACK, [5, 4]), Piece(Colour.BLACK, [5, 6])]

    def move_piece(self, piece, direction):
        # Piece already taken
        if piece.position == [-1, -1]:
            return False
        # Piece moving backwards illegally
        if direction == (MoveDirection.UP_RIGHT or MoveDirection.UP_LEFT) and piece.colour == Colour.BLACK and not piece.king:
            return False
        if direction == (MoveDirection.DOWN_RIGHT or MoveDirection.DOWN_LEFT) and piece.colour == Colour.WHITE and not piece.king:
            return False
        # Move blocked
        new_square = [sum(x) for x in zip(piece.position, [1, 1] if direction == MoveDirection.UP_RIGHT else
        [1, -1] if direction == MoveDirection.UP_LEFT else [-1, 1] if direction == MoveDirection.DOWN_RIGHT else [-1, -1])]
        # new square off the board
        if 0 > new_square[0] or new_square[0] > 7 or 0 > new_square[1] or new_square[1] > 7:
            return False
        # Can't move through square with own piece
        if self._board.state[new_square[0]][new_square[1]] == piece.colour:
            return False
        # Other colour
        if self._board.state[new_square[0]][new_square[1]] == piece.other_colour:
            jump_square = [sum(x) for x in zip(new_square, [1, 1] if direction == MoveDirection.UP_RIGHT else
        [1, -1] if direction == MoveDirection.UP_LEFT else [-1, 1] if direction == MoveDirection.DOWN_RIGHT else [-1, -1])]
            # can't jump off the board
            if 0 > jump_square[0] or jump_square[0] > 7 or 0 > jump_square[1] or jump_square[1] > 7:
                return False
            # Can't jump onto square with own piece
            if self._board.state[new_square[0]][new_square[1]] == piece.colour:
                return False
            # jump blocked
            if self._board.state[new_square[0]][new_square[1]] == piece.other_colour:
                return False
            # TODO: Do jump
            return True
        self._board.state[new_square[0]][new_square[1]] = piece.colour
        self._board.state[piece.position[0]][piece.position[1]] = Colour.BLANK
        piece.move(direction)
        return True

    # TODO:  Need to be able to check the direction that each piece is meant to be travelling in.  Guess white means up
    def check_take_avail(self, side):
        for i in range(8):
            for j in range(8):
                if self._board.state[i][j] == Colour.WHITE and side == Colour.WHITE:
                    if i < 6 and j < 6:
                        if self._board.state[i+1][j+1] == Colour.BLACK and self._board.state[i + 2][j + 2] == Colour.BLANK:
                            return True
                    if i < 6 and j > 1:
                        if self._board.state[i+1][j-1] == Colour.BLACK and self._board.state[i + 2][j - 2] == Colour.BLANK:
                            return True
                if self._board.state[i][j] == Colour.BLACK and side == Colour.BLACK:
                    if i > 1 and j < 6:
                        if self._board.state[i+1][j+1] == Colour.BLACK and self._board.state[i + 2][j + 2] == Colour.BLANK:
                            return True
                    if i > 1 and j > 1:
                        if self._board.state[i+1][j-1] == Colour.BLACK and self._board.state[i + 2][j - 2] == Colour.BLANK:
                            return True
        return False

    def check_blocked(self):
        for i in range(8):
            pass
from enum import Enum


class MoveType(Enum):
    MOVE = 1
    JUMP = 2


class Colour(Enum):
    BLANK = 1
    WHITE = 2
    BLACK = 3


class Direction(Enum):
    UP_RIGHT = 1  # [1, 1]
    UP_LEFT = 2   # [1, -1]
    DOWN_RIGHT = 3  # [-1, 1]
    DOWN_LEFT = 4  # [-1, -1]


class Piece:
    def __init__(self, colour, position):
        self._colour = colour
        self._position = position
        self._king = False
        self._direction = [Direction.UP_RIGHT, Direction.UP_LEFT] if colour == Colour.WHITE else \
            [Direction.DOWN_RIGHT, Direction.DOWN_LEFT]

    @property
    def colour(self):
        return self._colour

    def move(self, direction: Direction):
        self._position = Game.adj_square(self._position, direction)

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
        self._king = True

    def remove_piece(self):
        self._position = [-1, -1]


class Game:
    def __init__(self, Black_AIClass, White_AIClass):
        self._board = [[Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE],
                      [Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK],
                      [Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE, Colour.BLANK, Colour.WHITE],
                      [Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK],
                      [Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK, Colour.BLANK],
                      [Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK],
                      [Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK],
                      [Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK, Colour.BLACK, Colour.BLANK]]
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

    def check_move(self, piece, direction):
        # Piece already taken
        if piece.position == [-1, -1]:
            return False, None
        # Piece moving backwards illegally
        if direction == (Direction.UP_RIGHT or Direction.UP_LEFT) and piece.colour == Colour.BLACK and not piece.king:
            return False, None
        if direction == (Direction.DOWN_RIGHT or Direction.DOWN_LEFT) and piece.colour == Colour.WHITE and not piece.king:
            return False, None
        # Move blocked
        new_square = self.adj_square(piece.position, direction)
        # new square off the board
        if min(new_square) < 0 or max(new_square) > 7:
            return False, None
        # Can't move through square with own piece
        if self._board[new_square[0]][new_square[1]] == piece.colour:
            return False, None
        # Other colour
        if self._board[new_square[0]][new_square[1]] == piece.other_colour:
            jump_square = [sum(x) for x in zip(new_square, [1, 1] if direction == Direction.UP_RIGHT else
        [1, -1] if direction == Direction.UP_LEFT else [-1, 1] if direction == Direction.DOWN_RIGHT else [-1, -1])]
            # can't jump off the board
            if 0 > jump_square[0] or jump_square[0] > 7 or 0 > jump_square[1] or jump_square[1] > 7:
                return False, None
            # Can't jump onto square with any piece
            if self._board[new_square[0]][new_square[1]] != Colour.BLANK:
                return False, None
            return True, MoveType
        return True

    def make_move(self, piece, direction):
        allowed, m_type = self.check_move(piece, direction)
        if allowed:
            if m_type == MoveType.MOVE:
                self._board[piece.position[0]][piece.position[1]] = Colour.BLANK
                piece.move(direction)
                return True
            if m_type == MoveType.JUMP:
                new_square = self.adj_square(piece.position, direction)
                self._board[piece.position[0]][piece.position[1]] = Colour.BLANK
                self._board[new_square[0]][new_square[1]] = Colour.BLANK
                for piece in self._pieces[piece.other_colour]:
                    if piece.position == new_square:
                        piece.remove_piece()
                piece.move(direction)
                piece.move(direction)
                # TODO: multi jump
                if self.check_piece_can_take(piece):
                    pass
                return True
        return False

    def check_piece_can_take(self, piece: Piece):
        # Check 4 directions
        for element in Direction:
            if element not in piece.direction and not piece.king:
                # Can't take in the wrong direction
                continue
            new_square = self.adj_square(piece.position, element)
            jump_square = self.adj_square(new_square, element)
            # Check these squares are on the board
            if min(jump_square) < 0 or max(jump_square) > 8:
                continue
            if (self._board[new_square[0]][new_square[1]] == piece.other_colour and
               self._board[jump_square[0]][jump_square[1]] == Colour.BLANK):
                return True
        return False

    @staticmethod
    def adj_square(place, direc):
        return [sum(x) for x in zip(place, [1, 1] if direc == Direction.UP_RIGHT else
                [1, -1] if direc == Direction.UP_LEFT else
                [-1, 1] if direc == Direction.DOWN_RIGHT else [-1, -1])]

    def check_game_lost(self, colour):
        for piece in self._pieces[colour]:
            # The dead don't move
            if piece.position[0] < 0:
                continue
            if self.check_piece_can_take(piece):
                return True
            for direction in Direction:
                new_square = self.adj_square(piece.position, direction)
                if min(new_square) < 0 or max(new_square) > 7:
                    continue
                if direction not in piece.direction and not piece.king:
                    continue
                if self._board[new_square[0]][new_square[1]] == Colour.BLANK:
                    return True
        return False

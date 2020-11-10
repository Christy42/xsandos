from enum import Enum


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
    UP_RIGHT = 1  # [1, 1]
    UP_LEFT = 2   # [1, -1]
    DOWN_RIGHT = 3  # [-1, 1]
    DOWN_LEFT = 4  # [-1, -1]


class Piece:
    def __init__(self, colour, position):
        self._colour = colour
        self._position = position
        # Just kept for learning purposes
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
        self._direction = [Direction.UP_RIGHT, Direction.UP_LEFT, Direction.DOWN_RIGHT, Direction.DOWN_LEFT]
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

    def check_move(self, piece, direction):
        # Piece already taken
        if piece.position == [-1, -1]:
            return False, None
        # Piece moving backwards illegally
        if direction not in piece.direction:
            return False, None
        if direction not in piece.direction:
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
            jump_square = self.adj_square(new_square, direction)
            # can't jump off the board
            if min(jump_square) < 0 or max(jump_square) > 7:
                return False, None
            # Can't jump onto square with any piece
            if self._board[new_square[0]][new_square[1]] != Colour.BLANK:
                return False, None
            return True, MoveType.JUMP
        # Player must make a jump if required
        if self.check_jump_required(piece.colour):
            return False, None
        return True, MoveType.MOVE

    def make_move(self, piece, direction):
        allowed, m_type = self.check_move(piece, direction)
        if allowed:
            if m_type == MoveType.MOVE:
                self.turns_since_last_piece_taken += 1
                self._board[piece.position[0]][piece.position[1]] = Colour.BLANK
                piece.move(direction)
                if piece.position[0] in [0, 7]:
                    piece.king_piece()
                return True
            if m_type == MoveType.JUMP:
                self.turns_since_last_piece_taken = 0
                new_square = self.adj_square(piece.position, direction)
                self._board[piece.position[0]][piece.position[1]] = Colour.BLANK
                self._board[new_square[0]][new_square[1]] = Colour.BLANK
                for piece in self._pieces[piece.other_colour]:
                    if piece.position == new_square:
                        piece.remove_piece()
                piece.move(direction)
                piece.move(direction)
                # OK, bad abstraction here.  Should only be a king if in the last,
                # This is first and last how the only way to move to the first row is if already a king
                # making the same piece a king repeatedly has no effect. should be cleaner
                if piece.position[0] in [0, 7]:
                    piece.king_piece()
                # TODO: multi jump, must be done if possible
                if self.check_piece_can_take(piece):
                    # TODO: Force AI to make another move that involves this piece and a jump
                    pass
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
            if min(jump_square) < 0 or max(jump_square) > 8:
                continue
            if (self._board[new_square[0]][new_square[1]] == piece.other_colour and
               self._board[jump_square[0]][jump_square[1]] == Colour.BLANK):
                return True
        return False

    def check_jump_required(self, colour):
        for piece in self._pieces[colour]:
            if self.check_piece_can_take(piece):
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

    def start_game(self):
        blacks_turn = True
        while True:
            valid_move = False
            piece = self._pieces[Colour.WHITE][0]
            direction = Direction.DOWN_LEFT
            while not valid_move:
                if blacks_turn:
                    piece, direction = self._black_ai.move(must_jump=self.check_jump_required(Colour.BLACK),
                                                           ind_piece=None)
                else:
                    piece, direction = self._white_ai.move(must_jump=self.check_jump_required(Colour.BLACK),
                                                           ind_piece=None)
                valid_move = self.check_move(piece, direction)
            self.make_move(piece, direction)
            blacks_turn = not blacks_turn
            game_over = self.check_game_lost(Colour.BLACK if blacks_turn else Colour.WHITE)
            if game_over == Result.WHITE:
                print("White Win")
                return Result.WHITE
            if game_over == Result.BLACK:
                print("Black Win")
                return Result.BLACK
            if game_over == Result.DRAW:
                print("Draw")
                return Result.DRAW

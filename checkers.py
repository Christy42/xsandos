from game import Game
from enum import Enum


def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)


def sum_l(lister):
    ans = ''
    for element in lister:
        ans = ans + ', ' + element
    return ans[2:]


class MoveCheckers(Enum):
    PIECE = 1
    DIRECTION = 2


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


class Checkers(Game):
    def __init__(self, Black_AIClass=None, White_AIClass=None, board=None):
        super().__init__()
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
        self._ais = {Colour.BLACK: Black_AIClass(self, Colour.BLACK, Colour.WHITE), Colour.WHITE: White_AIClass(self, Colour.WHITE, Colour.BLACK)}

        self._turn = Colour.BLANK
        # TODO: Can we relate this to the board up above
        self._pieces = {Colour.WHITE: [], Colour.BLACK: []}
        for i in range(8):
            for j in range(8):
                if self._board[i][j] != Colour.BLANK:
                    self._pieces[self._board[i][j]].append(Piece(self._board[i][j], [i, j]))
        self.game_history = []
        self.add_state_to_game_history()

    def possible_moves(self, side: Colour, must_jump=False, ind_piece=None):
        possible_moves = []
        for piece in self._pieces[side]:
            if ind_piece:
                if ind_piece.position != piece.position:
                    continue
            for direction in Direction:
                if self.check_move({MoveCheckers.PIECE: piece, MoveCheckers.DIRECTION: direction})[0]:
                    possible_moves.append({MoveCheckers.PIECE: piece, MoveCheckers.DIRECTION: direction})
        return possible_moves

    def add_state_to_game_history(self):
        board_list = []
        for i in range(8):
            for j in range(8):
                position_char = ' '
                if self._board[i][j] == Colour.BLACK:
                    position_char = 'B'
                elif self._board[i][j] == Colour.WHITE:
                    position_char = 'W'
                board_list.append(position_char)
        board_string = ''.join(board_list)
        if self.game_history and self.game_history[-1] == board_string:
            # In the case of multiple jumps, we end up with multiple copies
            # of the board. Prune these here.
            return
        self.game_history.append(board_string)

    def print_board(self):
        for i in range(8):
            new_row = [colored(255 if self._board[i][j] != Colour.WHITE else 0,
                               255 if self._board[i][j] != Colour.BLACK else 0,
                               255 if self._board[i][j] == Colour.BLANK else 0, str(self._board[i][j])) for j in
                       range(8)]
            print(sum_l(new_row))

    @property
    def pieces(self):
        return self._pieces

    def check_move(self, move):
        # TODO: Double check that the right colour is being picked
        piece = move[MoveCheckers.PIECE]
        direction = move[MoveCheckers.DIRECTION]
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

    def make_move(self, move):
        # TODO: My god this hack is something horrific, this ensures that the piece selected is in this version of the
        # game.  Maybe the move should just include co-ordinates and not the piece object?
        piece = move[MoveCheckers.PIECE]
        for meeple in self._pieces[Colour.WHITE] + self._pieces[Colour.BLACK]:
            if meeple.position == piece.position:
                piece = meeple

        direction = move[MoveCheckers.DIRECTION]
        allowed, m_type = self.check_move(move)
        if allowed:
            if m_type == MoveType.MOVE:
                self.turns_since_last_piece_taken += 1
                self._board[piece.position[0]][piece.position[1]] = Colour.BLANK
                piece.move(direction)
                self._board[piece.position[0]][piece.position[1]] = piece.colour
                if piece.position[0] in [0, 7]:
                    piece.king_piece()
                self.add_state_to_game_history()
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
                        move = self._ais[piece.colour].move(must_jump=True, ind_piece=piece)
                        valid_move = self.check_move(move)
                    self.make_move(move)
                self.add_state_to_game_history()
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

    def check_end_game(self):
        if self._turn_count > 100:
            white_pieces = [piece for piece in self._pieces[Colour.WHITE] if piece.position[0] >= 0]
            black_pieces = [piece for piece in self._pieces[Colour.BLACK] if piece.position[0] >= 0]
            if len(white_pieces) > len(black_pieces):
                return Result.WHITE
            if len(black_pieces) > len(white_pieces):
                return Result.BLACK
            return Result.DRAW
        if self.turns_since_last_piece_taken >= 100:
            return Result.DRAW
        colour = self._turn
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

    @staticmethod
    def result_to_colour(result):
        return Colour.BLACK if result == Result.BLACK else Colour.WHITE

    @staticmethod
    def other_colour(colour):
        return Colour.BLACK if colour == Colour.WHITE else Colour.WHITE

    def start_game(self, verbose=False):
        self._turn = Colour.BLACK
        while True:
            self._turn_count += 1
            valid_move = False
            move = None
            while not valid_move:
                move = self._ais[self._turn].move(must_jump=self.check_jump_required(Colour.BLACK), ind_piece=None)
                valid_move, style = self.check_move(move)
            self.make_move(move)
            if verbose or self._turn_count > 1000:
                print("")
                print("")
                print("XXXXX")
                print(self._turn_count)
                print(self.turns_since_last_piece_taken)
                self.print_board()
            self._turn = Colour.WHITE if self._turn == Colour.BLACK else Colour.BLACK
            game_over = self.check_end_game()
            if game_over == Result.DRAW:
                if verbose:
                    print("Draw")
                self._ais[Colour.WHITE].draw()
                self._ais[Colour.BLACK].draw()
                return Result.DRAW
            if game_over:
                if verbose:
                    print(str(game_over).replace("Result.", "") + " Wins")
                self._ais[self.result_to_colour(game_over)].win()
                self._ais[self.other_colour(self.result_to_colour(game_over))].loss()
                return game_over


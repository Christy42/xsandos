from game import Game, GameRunner
from enum import Enum
from copy import deepcopy


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

    def to_colour(self):
        return Colour.BLACK if self.value == Result.BLACK else Colour.WHITE


class MoveType(Enum):
    MOVE = 1
    JUMP = 2


class Colour(Enum):
    BLANK = 1
    WHITE = 2
    BLACK = 3

    def other_colour(self):
        return Colour.BLACK if self.value == Colour.WHITE else Colour.WHITE

    def to_result(self):
        return Result.BLACK if self.value == Colour.BLACK else Result.WHITE
    

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

    def copy(self):
        piece_copy = Piece(self.colour, self.position[:])
        piece_copy._king = self._king
        piece_copy._direction = self._direction[:]
        return piece_copy
        
    @property
    def colour(self):
        return self._colour

    @property
    def is_dead(self):
        return self._position[0] < 0

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
    def __init__(self, board=None):
        super().__init__()
        if board:
            self._board = [[board[i] for i in range(j, j+8)] for j in [8 * k for k in range(8)]]
        else:
            self._next_player = Colour.BLACK
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
        self._piece_to_move = None

        # TODO: Can we relate this to the board up above
        self._pieces = {Colour.WHITE: [], Colour.BLACK: []}
        for i in range(8):
            for j in range(8):
                if self._board[i][j] != Colour.BLANK:
                    self._pieces[self._board[i][j]].append(Piece(self._board[i][j], [i, j]))
        self.game_history = []
        self.add_state_to_game_history()

    @property
    def turn_count(self):
        return self._turn_count

    @property
    def piece_to_move(self):
        return self._piece_to_move

    def copy(self, include_history=True):
        game_copy = Checkers()
        for i in range(len(game_copy._board)):
            game_copy._board[i] = self._board[i][:]
        game_copy._next_player = self._next_player
        game_copy._turn_count = self._turn_count
        game_copy._piece_to_move = self._piece_to_move
        game_copy.turns_since_last_piece_taken = self.turns_since_last_piece_taken

        game_copy._pieces = {}
        for key in self._pieces:
            game_copy._pieces[key] = [p.copy() for p in self._pieces[key]]

        game_copy.game_history = []
        if include_history:
            game_copy.game_history = deepcopy(self.game_history)
        return game_copy
            
    def possible_moves(self, side: Colour):
        possible_moves = []
        for piece in self._pieces[side]:
            if self._piece_to_move:
                if self._piece_to_move.position != piece.position:
                    continue
            for direction in Direction:
                if self.check_move({MoveCheckers.PIECE: piece, MoveCheckers.DIRECTION: direction})[0]:
                    possible_moves.append({MoveCheckers.PIECE: piece, MoveCheckers.DIRECTION: direction})
        return possible_moves

    def add_state_to_game_history(self):
        board_list = []
        for i in range(8):
            for j in range(8):
                position_char = 'B' if self._board[i][j] == Colour.BLACK else \
                    'W' if self._board[i][j] == Colour.WHITE else ' '
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
        print([val.position for val in self._pieces[Colour.WHITE]])
        print(self._pieces[Colour.WHITE])
        print([val.position for val in self._pieces[Colour.BLACK]])
        print(self._pieces[Colour.BLACK])

    @property
    def pieces(self):
        return self._pieces

    def check_move(self, move):
        # TODO: Double check that the right colour is being picked
        # print("AAAAAAAAAAAAAAAA")
        # print(move)
        piece = move[MoveCheckers.PIECE]
        direction = move[MoveCheckers.DIRECTION]
        # Check if double jump required
        if self._piece_to_move:
            if self._piece_to_move.position != piece.position:
                return False, None
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
        if not allowed:
            return False

        if m_type == MoveType.MOVE:
            self.turns_since_last_piece_taken += 1
            self._board[piece.position[0]][piece.position[1]] = Colour.BLANK
            piece.move(direction)
            self._board[piece.position[0]][piece.position[1]] = piece.colour
            if piece.position[0] in [0, 7]:
                piece.king_piece()
        elif m_type == MoveType.JUMP:
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
        else:
            # raise NotImplementedError("Unknown move type {}".format(m_type))
            print('Unknown move type {}'.format(m_type))
            return False
            
        if m_type == MoveType.MOVE or not self.check_piece_can_take(piece):
            self._turn_count += 1
            self._next_player = Colour.WHITE if self._next_player == Colour.BLACK else Colour.BLACK
            self._piece_to_move = None
            # valid_move = False
            # while not valid_move:
            #    move = self._ais[piece.colour].move(must_jump=True, ind_piece=piece)
            #    print(self._ais[piece.colour].id_val)
            #    print("")
            #    print(move)
            #    print(move[MoveCheckers.PIECE].position)
            #    print([pi.position for pi in self._pieces[self._turn]])
            #    valid_move = self.check_move(move)
            #    print(valid_move)
            # self.make_move(move)
        else:
            self._piece_to_move = piece
        self.add_state_to_game_history()
        return True

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
        return [place[0] + (1 if direc in [Direction.DOWN_RIGHT, Direction.DOWN_LEFT] else -1),
                place[1] + (1 if direc in [Direction.UP_RIGHT, Direction.DOWN_RIGHT] else -1)]

    def check_end_game(self):
        if self._turn_count > 100:
            white_pieces = [piece for piece in self._pieces[Colour.WHITE] if not piece.is_dead]
            black_pieces = [piece for piece in self._pieces[Colour.BLACK] if not piece.is_dead]
            if len(white_pieces) > len(black_pieces):
                return Result.WHITE
            if len(black_pieces) > len(white_pieces):
                return Result.BLACK
            return Result.DRAW
        if self.turns_since_last_piece_taken >= 100:
            return Result.DRAW
        colour = self._next_player
        for piece in self._pieces[colour]:
            # The dead don't move
            if piece.is_dead:
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
        return colour.to_result()


class CheckersRunner(GameRunner):
    def __init__(self, Black_AIClass=None, White_AIClass=None):
        super().__init__()
        self._game = Checkers()
        self._ais = {
            Colour.BLACK: Black_AIClass(self._game, Colour.BLACK, Colour.WHITE),
            Colour.WHITE: White_AIClass(self._game, Colour.WHITE, Colour.BLACK),
        }
        
    def start_game(self, verbose=False):
        while True:
            valid_move = False
            move = None
            while not valid_move:
                next_ai = self._ais[self._game.next_player]
                move = next_ai.move(must_jump=self._game.check_jump_required(Colour.BLACK),
                                    ind_piece=self._game.piece_to_move)  # TODO: arg
                valid_move, style = self._game.check_move(move)
            self._game.make_move(move)
            if verbose or self._game.turn_count > 1000:  # TODO: make property
                print("")
                print("")
                print("X X X X X")
                print(self._game.turn_count)
                print(self._game.turns_since_last_piece_taken)
                self._game.print_board()
            game_over = self._game.check_end_game()
            if game_over == Result.DRAW:
                if verbose:
                    print("Draw")
                self._ais[Colour.WHITE].draw()
                self._ais[Colour.BLACK].draw()
                return Result.DRAW
            if game_over:
                if verbose:
                    print(str(game_over).replace("Result.", "") + " Wins")
                winning_colour = game_over.to_colour()
                self._ais[winning_colour].win()
                self._ais[winning_colour.other_colour()].loss()
                return game_over

    def game_history(self):
        return self._game.game_history

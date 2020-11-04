from enum import Enum


class Result(Enum):
    Xs = 1
    Os = 2
    DRAW = 3


class Square(Enum):
    BLANK = 1
    Xs = 2
    Os = 3


class Game:
    def __init__(self):
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

    def start_game(self):
        xs_turn = True
        for i in range(9):
            valid_move = False
            row, col = 0, 0
            while not valid_move:
                if xs_turn:
                    row, col = xs_ai(self)
                else:
                    row, col = xs_ai(self)
                valid_move = True if self._squares[row][col] == Square.BLANK else False
            self._squares[row][col] = Square.Xs if xs_turn else Square.Os
            xs_turn = not xs_turn
            game_over = self.check_win()
            if game_over == Square.Xs:
                print("X Win")
                for k in range(3):
                    print(self._squares[k])
                return Result.Xs
            if game_over == Square.Os:
                print("O Win")
                for k in range(3):
                    print(self._squares[k])
                return Result.Os
        print("Draw")
        for k in range(3):
            print(self._squares[k])
        return Result.DRAW


def xs_ai(game: Game):
    for i in range(3):
        for j in range(3):
            if game.squares[i][j] == Square.BLANK:
                return i, j

b = Game()
b.start_game()

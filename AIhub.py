import random
from math import inf
from copy import deepcopy
from checkers import Colour
from game import Game


class RandomAI:
    def __init__(self, game, side, other_side):
        self._game = game
        self._side = side

    def move(self, **kwargs):
        return random.choice(self._game.possible_moves(self._side))

    def win(self):
        pass

    def draw(self):
        pass

    def loss(self):
        pass


class StateLearnerAI:
    states_seen = {}
    states_won = {}
    states_drawn = {}
    states_lost = {}

    def __init__(self, game, side, other_side):
        self._game = game
        self._side = side
        self._other_side = other_side
        self._temp_game = game
        self.id_val = 2

    def move(self, **kwargs):
        move = self.get_best_historical_move(**kwargs)
        return move

    def get_position_rating(self, board_tuple):
        if board_tuple not in self.states_seen:
            return 0
        num_times_seen = self.states_seen[board_tuple]
        num_times_won = self.states_won[board_tuple]
        num_times_drawn = self.states_drawn[board_tuple]
        num_times_lost = self.states_lost[board_tuple]

        return (num_times_won * 3. + num_times_drawn - 200 * num_times_lost) / num_times_seen

    def get_best_historical_move(self, **kwargs):
        best_move = None
        best_ranking = None
        pos_moves = self._game.possible_moves(self._side, **kwargs)
        # TODO: This is a bit of a hack to deal with the second move for checkers
        temp_game_used = False
        if len(pos_moves) == 0:
            pos_moves = self._temp_game.possible_moves(self._side, **kwargs)
            temp_game_used = True  # if we are basing possible moves off of temp game we should build from that
        for move in pos_moves:
            if temp_game_used:
                self._temp_game = self._temp_game.g_deepcopy(self._game.ais)
            else:
                del self._temp_game
                self._temp_game = self._game.g_deepcopy(self._game.ais)
            self._temp_game.make_move(deepcopy(move))
            pos_ranking = self.get_position_rating(self.get_board_tuple(self._temp_game))
            if best_ranking is None or pos_ranking > best_ranking:
                best_move = move
                best_ranking = pos_ranking
        return best_move

    def get_board_tuple(self, game):
        board_list = []
        for i in range(len(game.board)):
            for j in range(len(game.board[i])):
                square = ' '
                if game.board[i][j] == self._side:
                    square = 'M'  # my square
                elif game.board[i][j] != self._other_side:
                    square = 'E'  # enemy square
                board_list.append(square)
        return tuple(board_list)

    def win(self):
        self.update_num_seen()
        for state in self._game.game_history:
            self.states_won[state] += 1

    def draw(self):
        self.update_num_seen()
        for state in self._game.game_history:
            self.states_drawn[state] += 1

    def loss(self):
        self.update_num_seen()
        for state in self._game.game_history:
            # print('Recording: {}'.format(state))
            self.states_lost[state] += 1

    def update_num_seen(self):
        for state in self._game.game_history:
            if state not in self.states_seen:
                self.states_seen[state] = 1
                self.states_won[state] = 0
                self.states_drawn[state] = 0
                self.states_lost[state] = 0


class ProjectedStateLearnerAI(StateLearnerAI):
    def get_board_state(self, board):
        my_piece_count, their_piece_count = 0, 0
        for i in range(8):
            for j in range(8):
                if board[i][j] == self._side:
                    my_piece_count += 1
                elif board[i][j] != Colour.BLANK:
                    their_piece_count += 1
        return (my_piece_count - their_piece_count,)


class AlphaBetaAI:
    def __init__(self, game, side, other_side):
        self._game = game
        self._side = side
        self._other_side = other_side
        self._temp_game = game
        self.id_val = 1

    def move(self, **kwargs):
        print("alpha beta move")
        best_move = None
        best_value = -inf
        pos_moves = self._game.possible_moves(self._side, **kwargs)
        temp_game_used = False
        # TODO: This is a bit of a hack to deal with the second move for checkers
        if len(pos_moves) == 0:
            pos_moves = self._temp_game.possible_moves(self._side, **kwargs)
            temp_game_used = True  # if we are basing possible moves off of temp game we should build from that
        print(pos_moves)
        if len(pos_moves) == 0:
            print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
            print([value for value in kwargs.values()][1].position)
            self._game.print_board()
            print("")
            self._temp_game.print_board()
        print([value for value in kwargs.values()])
        print("Loop Start")
        for move in pos_moves:
            # Could depth be optimised by if we have to jump or use a specific piece as there are less options
            if temp_game_used:
                self._temp_game = self._temp_game.g_deepcopy(self._game.ais)  # possible memory leak (small)?
            else:
                del self._temp_game
                self._temp_game = self._game.g_deepcopy(self._game.ais)

            # print(move)
            # print("HHHHHHHHHHHHHHHHH")
            self._temp_game.make_move(deepcopy(move))
            new_value = self.alphabeta(self._temp_game, 3, -inf, inf, True, **kwargs)
            # print("QQQQQQQQQQQQQQQQQQQQQQQQQQQ")
            # print(new_value)
            # print(best_value)
            if new_value >= best_value:
                best_move = move
                best_value = new_value
        # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        # print(pos_moves)
        # print(best_move)
        # print("alpha beta finished")
        return best_move

    def alphabeta(self, node: Game, depth: int, alpha: int, beta: int, maximizing_player: bool, **kwargs):
        if depth == 0 or self._game.check_end_game():
            total = 0
            # TODO: Have this sub-function as an input into the AI so it can be more general
            # Should probably value a 0 from one side far more heavily
            for piece in node.pieces[self._side]:
                total += 0 if piece.is_dead else 5 if piece.king else 3
            for piece in node.pieces[self._other_side]:
                total -= 0 if piece.is_dead else 5 if piece.king else 3
            return total + random.random()  # random values are try and ensure that ties get picked differently

        if maximizing_player:
            value = -inf
            for child in node.possible_moves(side=self._side, **kwargs):  # need child to be something sensible here
                del self._temp_game
                # print(node.possible_moves(side=self._other_side, **kwargs))
                # print(val for val in kwargs)
                # print(child)
                # print("XXXXXX")
                self._temp_game = self._game.g_deepcopy(self._game.ais)
                self._temp_game.make_move(deepcopy(child))
                value = max(value, self.alphabeta(self._temp_game, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    return value + random.random()
            return value + random.random()
        else:
            value = +inf
            for child in node.possible_moves(side=self._other_side, **kwargs):
                # print(node.possible_moves(side=self._other_side, **kwargs))
                # print(val for val in kwargs)
                # print(child)
                # print("YYYYYYY")
                del self._temp_game
                self._temp_game = self._game.g_deepcopy(self._game.ais)
                self._temp_game.make_move(deepcopy(child))
                value = min(value, self.alphabeta(self._temp_game, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    return value + random.random()
            return value + random.random()

    def win(self):
        pass

    def draw(self):
        pass

    def loss(self):
        pass

import random
from math import inf
from copy import deepcopy
from checkers import Colour


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
        if len(pos_moves) == 0:
            pos_moves = self._temp_game.possible_moves(self._side, **kwargs)
        for move in pos_moves:
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


class AlphaBeta:
    def __init__(self, game, side, other_side):
        self._game = game
        self._side = side
        self._other_side = other_side

    def move(self, **kwargs):
        return random.choice(self._game.possible_moves(self._side))

    def alphabeta(self, node, depth, alpha, beta, maximizingPlayer):
        if depth == 0 or self._game.check_end_game():
            return 0

        if maximizingPlayer:
            value = -inf
            for child in node:
                value = max(value, self.alphabeta(child, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    # (*β cutoff *)
                    return value
        else:
            value = +inf
            for child in node:
                value = min(value, self.alphabeta(child, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if beta >= alpha:
                    # (*α cutoff *)
                    return value

    def win(self):
        pass

    def draw(self):
        pass

    def loss(self):
        pass
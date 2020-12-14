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
        assert len(pos_moves) > 0

        for move in pos_moves:
            temp_game = self._game.copy(include_history=False) #deepcopy(self._game)
            temp_game.make_move(move)
            pos_ranking = self.get_position_rating(self.get_board_tuple(temp_game))
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
        best_move = None
        best_value = -inf
        pos_moves = self._game.possible_moves(self._side)

        assert len(pos_moves) > 0

        for move in pos_moves:
            # Could depth be optimised by if we have to jump or use a specific piece as there are less options
            temp_game = self._game.copy(include_history=False)  # deepcopy(self._game)
            temp_game.make_move(deepcopy(move))
            new_value = self.alphabeta(temp_game, 3, -inf, inf, temp_game.next_player == self._side, **kwargs) + \
                            random.random()
            if new_value >= best_value:
                best_move = move
                best_value = new_value
        assert best_move is not None
        return best_move

    def value_func(self, node):
        total = 0
        # TODO: Have this sub-function as an input into the AI so it can be more general
        # Should probably value a 0 from one side far more heavily
        for piece in node.pieces[self._side]:
            total += 0 if piece.is_dead else 5 if piece.king else 3
        for piece in node.pieces[self._other_side]:
            total -= 0 if piece.is_dead else 5 if piece.king else 3
        return total  # random values are try and ensure that ties get picked differently

    def alphabeta(self, node: Game, depth: int, alpha: int, beta: int, maximizing_player: bool, **kwargs):
        if depth == 0 or node.check_end_game():
            return self.value_func(node)

        if maximizing_player:
            value = -inf
            for child in node.possible_moves(side=self._side):  # need child to be something sensible here
                temp_game = node.copy(include_history=False)  # deepcopy(node)
                temp_game.make_move(deepcopy(child))
                value = max(value, self.alphabeta(temp_game, depth - 1, alpha, beta, temp_game.next_player == self._side))
                alpha = max(alpha, value)
                if alpha >= beta:
                    return value  # + random.random()
            return value  # + random.random()
        else:
            value = +inf
            for child in node.possible_moves(side=self._other_side):
                temp_game = node.copy(include_history=False)  # deepcopy(node)
                temp_game.make_move(deepcopy(child))
                value = min(value, self.alphabeta(temp_game, depth - 1, alpha, beta, temp_game.next_player == self._side))
                beta = min(beta, value)
                if beta <= alpha:
                    return value  # + random.random()
            return value  # + random.random()

    def win(self):
        pass

    def draw(self):
        pass

    def loss(self):
        pass


class AlphaBeta2(AlphaBetaAI):
    def __init__(self, game, side, other_side):
        super().__init__(game, side, other_side)

    def value_func(self, node):
        total = 0
        # TODO: Have this sub-function as an input into the AI so it can be more general
        # Should probably value a 0 from one side far more heavily
        check = 0
        for piece in node.pieces[self._side]:
            check += 0 if piece.is_dead else 5 if piece.king else 3
        total += check
        if check == 0:
            total -= 200
        check = 0
        for piece in node.pieces[self._other_side]:
            check -= 0 if piece.is_dead else 5 if piece.king else 3
        total += check
        if check == 0:
            total += 200
        return total

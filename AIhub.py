import random
from copy import deepcopy
from xsandos import MoveXs


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
        self.this_game_states = []

    def move(self, **kwargs):
        board_tuple = self.get_board_tuple(self._game)
        move = self.get_best_historical_move(**kwargs)
        board_list = list(board_tuple)
        board_list[move[MoveXs.ROW] * len(self._game.board) + move[MoveXs.COLUMN]] = 'M'
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

    def get_best_historical_move(self, **kwargs):
        best_move = None
        best_ranking = None
        pos_moves = self._game.possible_moves(self._side, **kwargs)
        for move in pos_moves:
            temp_game = deepcopy(self._game)
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

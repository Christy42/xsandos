import random
from math import inf
from copy import deepcopy
from checkers import Colour
from game import Game

import pickle
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import cross_val_score, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from keras.models import load_model


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

def build_model():
    model = Sequential()
    model.add(Dense(8*4, input_dim=8*4, kernel_initializer='normal', activation='relu'))
    model.add(Dense(8, kernel_initializer='normal', activation='relu'))
    model.add(Dense(6, kernel_initializer='normal', activation='relu'))
    model.add(Dense(1, kernel_initializer='normal'))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model

# HACK: we only want to load this model once for performance reasons, so make it global.
# will tidy later...
model_pipeline = None
class NeuralNetMoveScoreAI:
    def __init__(self, game, side, other_side):
        self._game = game
        self._side = side
        self._other_side = other_side
        self._temp_game = game
        global model_pipeline
        if model_pipeline is None:
            model_pipeline = self.train_model(1, 'games_dump/dump_ab.pkl', 1)
            model_pipeline.named_steps['mlp'].model = load_model('mlp.h5')
        self.pipeline = model_pipeline

    def string_to_array(self, board_string):
        board_array = np.zeros((8, 8), dtype='int')
        for i in range(8):
            for j in range(8):
                val = 0
                if board_string[i*8+j] == 'W':
                    val = 2
                elif board_string[i*8+j] == 'B':
                    val = -2
                elif board_string[i*8+j] == 'w':
                    val = 1
                elif board_string[i*8+j] == 'b':
                    val = -1
                board_array[i, j] = val
        return board_array

    def array_to_list(self, board_array):
        board_list = np.zeros(4*8, dtype='int')
        pos = 0
        for i in range(8):
            for j in range(8):
                # Only encode squares that may contain pieces:
                if (i+j) % 2 == 0:
                    continue
                board_list[pos] = board_array[i, j]
                pos += 1
        return board_list
        
    def train_model(self, train_set_size, data_fname, epochs):        
        alphabeta_inputs = []
        alphabeta_outputs = []
        with open(data_fname, 'rb') as f:
            alphabeta_data = pickle.load(f)
            for b,val in alphabeta_data.items():
                board_arr = self.string_to_array(b)
                alphabeta_inputs.append(self.array_to_list(board_arr))
                alphabeta_outputs.append(val)

        # Train model:
        estimators = list()
        estimators.append(('standardize', StandardScaler()))
        estimators.append(('mlp', KerasRegressor(build_fn=build_model, epochs=epochs, batch_size=5, verbose=0)))
        
        pipeline = Pipeline(estimators)
        kfold = KFold(n_splits=10)
        return pipeline.fit(alphabeta_inputs[:train_set_size], np.array(alphabeta_outputs[:train_set_size]))

    def get_board_value_from_model(self, temp_game_string):
        temp_game_array = self.string_to_array(temp_game_string)
        temp_game_list = self.array_to_list(temp_game_array)
        prediction = self.pipeline.predict([temp_game_list])
        return prediction
        
    def move(self, **kwargs):
        best_move = None
        best_value = -inf
        pos_moves = self._game.possible_moves(self._side)

        assert len(pos_moves) > 0

        global board_to_value
        for move in pos_moves:
            # Could depth be optimised by if we have to jump or use a specific piece as there are less options
            temp_game = self._game.copy(include_history=False)  # deepcopy(self._game)
            temp_game.make_move(deepcopy(move))
            temp_game_string = temp_game.as_string()
            new_value = self.get_board_value_from_model(temp_game_string)
            if new_value >= best_value:
                best_move = move
                best_value = new_value
            board_to_value[temp_game_string] = new_value
        assert best_move is not None
        return best_move

    def win(self):
        pass

    def draw(self):
        pass

    def loss(self):
        pass


        
# HACK: save moves for training... will remove this
board_to_value = {}

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

        global board_to_value
        for move in pos_moves:
            # Could depth be optimised by if we have to jump or use a specific piece as there are less options
            temp_game = self._game.copy(include_history=False)  # deepcopy(self._game)
            temp_game.make_move(deepcopy(move))
            temp_game_string = temp_game.as_string()
            new_value = self.alphabeta(temp_game, 3, -inf, inf, temp_game.next_player == self._side, **kwargs) + \
                            random.random()
            if new_value >= best_value:
                best_move = move
                best_value = new_value
            board_to_value[temp_game_string] = new_value
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

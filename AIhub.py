import random


class RandomAI:
    def __init__(self, game, side):
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

    def move(self):
        board_tuple = self.get_board_tuple()
        move = self.get_best_historical_move(board_tuple)
        board_list = list(board_tuple)
        board_list[move[0] * 3 + move[1]] = 'M'
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

    def get_best_historical_move(self, board_tuple):
        best_pos = None
        best_ranking = None
        board_list = list(board_tuple)
        # TODO: Only goes through 9 values....
        for pos in range(9):
            if board_list[pos] != ' ':
                continue
            board_list[pos] = 'M'
            pos_ranking = self.get_position_rating(tuple(board_list))
            board_list[pos] = ' '
            if best_ranking is None or pos_ranking > best_ranking:
                best_pos = pos
                best_ranking = pos_ranking
        # TODO: // 3 will be an issue with board size
        return best_pos // 3, best_pos % 3

    def get_board_tuple(self):
        board_list = []
        for i in range(self._game._board):
            for j in range(3):
                square = ' '
                if self._game.squares[i][j] == self._side:
                    square = 'M'  # my square
                elif self._game.squares[i][j] != self._other_side:
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

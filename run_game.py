import os, pickle


from checkers import Checkers, Result
from xsandos import XsAndOs, NewellSimonAI
from AIhub import *


game = "checkers"

if game == "xsandos":
    print('X - NewellSimonAI; O - StateLearnerAI')
    for i in range(50):
        b = XsAndOs(NewellSimonAI, StateLearnerAI)
        b.start_game(verbose=False)

    print('\n\nX - StateLearnerAI; O - NewellSimonAI')
    for i in range(30):
        b = XsAndOs(StateLearnerAI, NewellSimonAI)
        b.start_game(verbose=False)

    print('\n\nX - StateLearnerAI; O - StateLearnerAI')
    for i in range(1):
        b = XsAndOs(StateLearnerAI, StateLearnerAI)
        b.start_game(verbose=True)

    print('\n\nX - RandomAI; O - StateLearnerAI')
    for i in range(1):
        b = XsAndOs(RandomAI, StateLearnerAI)
        b.start_game(verbose=True)

if game == "checkers":
    # checkers = Checkers(Black_AIClass=RandomAI, White_AIClass=StateLearnerAI)
    # checkers.start_game(verbose=False)
    black_class = AlphaBetaAI
    white_class = StateLearnerAI
    print('\n\nBlack: {}; White: {}'.format(black_class.__name__, white_class.__name__))
    wins = 0
    losses = 0
    draws = 0

    save_game_history = False

    game_record_output_dir = 'games_dump'
    if not os.path.exists(game_record_output_dir):
        os.makedirs(game_record_output_dir)
    game_histories = []
    game_wins = []

    for i in range(1):
        if i % 10 == 0 and i > 0:
            print(
                "Stats: {:5.4f}-{:5.4f}-{:5.4f} (wins-draws-losses) ... {}".format(wins / i, draws / i, losses / i, i))

            if save_game_history:
                dump_filename = os.path.join(game_record_output_dir, 'dump_{}.pkl'.format(i))
                with open(dump_filename, 'wb') as f:
                    pickle.dump((game_wins, game_histories), f)
                    game_wins = []
                    game_histories = []

        b = Checkers(Black_AIClass=black_class, White_AIClass=white_class)
        win = b.start_game(verbose=True)
        if win == Result.BLACK:
            wins += 1
            winner = 'BLACK'
        elif win == Result.WHITE:
            losses += 1
            winner = 'WHITE'
        else:
            draws += 1
            winner = 'DRAW'
        game_wins.append(winner)
        game_histories.append(b.game_history)


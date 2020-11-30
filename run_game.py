from checkers import Checkers, MoveCheckers
from xsandos import MoveXs, XsAndOs, NewellSimonAI
from AIhub import *


print('X - NewellSimonAI; O - StateLearnerAI')
for i in range(50):
    b = XsAndOs(RandomAI, RandomAI)
    b.start_game(verbose=False)

print('\n\nX - StateLearnerAI; O - NewellSimonAI')
for i in range(30):
    b = XsAndOs(RandomAI, NewellSimonAI)
    b.start_game(verbose=False)

print('\n\nX - StateLearnerAI; O - StateLearnerAI')
for i in range(30):
    b = XsAndOs(RandomAI, RandomAI)
    b.start_game(verbose=False)

print('\n\nX - RandomAI; O - StateLearnerAI')
for i in range(1):
    b = XsAndOs(RandomAI, RandomAI)
    b.start_game(verbose=True)




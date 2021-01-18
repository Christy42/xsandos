from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor
from sklearn.model_selection import cross_val_score, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


import os
import pickle
import numpy as np


def string_to_array(board_string):
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


def count_adj(board_arr):
    adj_count = 0
    for i in range(8-1):
        for j in range(8):
            if j-1 > 0 and board_arr[i+1, j-1] * board_arr[i, j] == -1:
                adj_count += 1
            if j+1 < 8 and board_arr[i+1, j+1] * board_arr[i, j] == -1:
                adj_count += 1
    return adj_count


def alphabeta_count(board_arr):
    count = 0
    for i in range(8):
        for j in range(8):
            count += (3 if board_arr[i][j] == 1 else (5 if board_arr[i][j] == 2 else (-3 if board_arr[i][j] == -1 else (-5 if board_arr[i][j] == -2 else 8))))
    return count


def array_to_list(board_array):
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


def get_input_outputs_for_fname(fname):
    inputs = []
    outputs = []
    _, boards = pickle.load(open(fname, 'rb'))
    for board in boards:
        for b in board:
            board_arr = string_to_array(b)
            adj = alphabeta_count(board_arr)
            # adj = count_adj(board_arr)
            arr_list = array_to_list(board_arr)
            inputs.append(arr_list)
            outputs.append(adj)
    return inputs, outputs


def build_model():
    model = Sequential()
    model.add(Dense(8*4, input_dim=8*4, kernel_initializer='normal', activation='relu'))
    model.add(Dense(8, kernel_initializer='normal', activation='relu'))
    model.add(Dense(6, kernel_initializer='normal', activation='relu'))
    model.add(Dense(1, kernel_initializer='normal'))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model

#input_val = []
#output = []
#for f_name in os.listdir('games_dump'):
#    inp, out = get_input_outputs_for_fname(os.path.join('games_dump', f_name))
#    input_val += inp
#    output += out

alphabeta_inputs = []
alphabeta_outputs = []
f_name = os.path.join('games_dump', 'dump_ab.pkl')
with open(f_name, 'rb') as f:
    alphabeta_data = pickle.load(f)
    for b,val in alphabeta_data.items():
        board_arr = string_to_array(b)
        alphabeta_inputs.append(array_to_list(board_arr))
        alphabeta_outputs.append(val)

# Train model:
train_set_size = 60000
estimators = list()
estimators.append(('standardize', StandardScaler()))
estimators.append(('mlp', KerasRegressor(build_fn=build_model, epochs=1000, batch_size=5, verbose=0)))
pipeline = Pipeline(estimators)
kfold = KFold(n_splits=10)
# results = cross_val_score(pipeline, inputs[:10000], np.array(outputs[:10000]), cv=kfold)

#fit_model = pipeline.fit(input_val[:10000], np.array(output[:10000]))
fit_model = pipeline.fit(alphabeta_inputs[:60000], np.array(alphabeta_outputs[:60000]))

# UNCOMENT OUT TO LOAD
#from keras.models import load_model
#fit_model.named_steps['mlp'].model = load_model('mlp.h5')

# Score on out-of-training-sample data
#out_of_sample_score = fit_model.score(input_val[10000:20000], np.array(output[10000:20000]))
#out_of_sample_predictions = fit_model.predict(input_val[10000:20000])

out_of_sample_score = fit_model.score(alphabeta_inputs[60000:], np.array(alphabeta_outputs[60000:]))
out_of_sample_predictions = fit_model.predict(alphabeta_inputs[60000:])

fit_model.named_steps['mlp'].model.save('mlp.h5')


print(out_of_sample_score)
print(abs(np.array(alphabeta_outputs[60000:])).mean())
print(abs(out_of_sample_predictions - np.array(alphabeta_outputs[60000:])).mean())
print(abs(np.array(alphabeta_outputs[60000:])).mean())
print(abs(out_of_sample_predictions - np.array(alphabeta_outputs[60000:])).mean())

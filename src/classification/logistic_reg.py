import argparse
import heapq

from keras.models import Sequential
from keras.layers import Dense
import numpy as np

from image_data import ImageDataKFold


def average_weights_and_biases(w, b):
    return np.average(w, axis=0), np.average(b, axis=0)


def get_model(in_dim, out_dim):
    model = Sequential()
    model.add(Dense(out_dim, input_dim=in_dim))
    model.compile(optimizer='rmsprop', loss='mse', metrics=['accuracy'])
    return model


def get_most_significant_weight_idx(weights, num=10):
    abs_weights = [[abs(i) for i in w] for w in weights]
    items = ((sum(abs_weights[i]), i) for i in range(len(abs_weights)))
    return heapq.nlargest(num, items, key=lambda x: x[0])


def evaluate_predictions(y_true, y_pred, pred_thresh):
    prediction_acc = []
    n_false_pos = 0

    for i in range(len(y_true)):

        # 1-hot output, i.e. [totality, not_totality]
        if len(y_true.shape) > 1:
            true_idx = y_true[i].argmax()
            pred_idx = y_pred[i].argmax()

            if pred_thresh is None or (y_pred[pred_idx][0] >= pred_thresh):
                prediction_acc.append(int(pred_idx == true_idx))
                n_false_pos += int(pred_idx == 0 and pred_idx != true_idx)

        # binary output, i.e. 1 => totality, 0 => not_totality
        else:
            true_val = y_true[i]
            pred_val = y_pred[i][0]

            if pred_thresh is None or (pred_val >= pred_thresh or pred_val <= (1 - pred_thresh)):
                true_val = int(true_val)
                pred_val = round(pred_val)
                prediction_acc.append(int(true_val == pred_val))
                n_false_pos += int(pred_val == 1 and pred_val != true_val)

    # It is possible that we set pred_thresh too high and all predictions are rejected
    try:
        acc = sum(prediction_acc) / float(len(prediction_acc))
    except ZeroDivisionError:
        acc = 0

    num_test_cases = len(y_true)
    num_accepted = len(prediction_acc)
    accept_ratio = num_accepted / float(num_test_cases)
    false_pos_ratio = n_false_pos / float(num_test_cases)

    print('\n------------------')
    print('Model Performance:')
    print('------------------')
    print('Total number of test cases: {}'.format(len(y_true)))
    print('Number of accepted test cases: {}'.format(len(prediction_acc)))
    print('Accuracy: {}'.format(acc))
    print('False positive ratio (n_false_pos / total_num_test_cases): {}'.format(false_pos_ratio))

    return acc, false_pos_ratio, accept_ratio


def main():
    parser = argparse.ArgumentParser(description='Totality image classifier')
    parser.add_argument('--pred-type', type=str, default='onehot')
    parser.add_argument('--pred-thresh', type=float, default=None)
    args = parser.parse_args()

    # Get data
    dataset = ImageDataKFold(nfolds=10, one_hot=(args.pred_type == 'onehot'))
    in_dim, out_dim = dataset.get_dim()

    results = list()
    weights, biases = list(), list()
    for train, test in dataset.get_folds():

        x_train, y_train = train
        x_test, y_test = test

        # Build and train model
        model = get_model(in_dim, out_dim)
        model.fit(x_train, y_train, nb_epoch=10)

        # Save weights
        w, b = model.layers[0].get_weights()
        weights.append(w)
        biases.append(b)

        # Test model
        y_pred = model.predict(x_test)
        res = evaluate_predictions(y_test, y_pred, args.pred_thresh)

        results.append(res)

    acc, false_pos_ratio, accept_ratio = np.average(results, axis=0)

    print('\n--------------------')
    print('Overall Performance:')
    print('--------------------')
    print('\tAccuracy:             {}'.format(acc))
    print('\tFalse positive ratio: {}'.format(false_pos_ratio))
    print('\tAcceptance ratio:     {}'.format(accept_ratio))

    # Get most significant weights
    weights, bias = average_weights_and_biases(weights, biases)
    top10 = get_most_significant_weight_idx(weights, 10)

    print('\n--------------------------------------------------------------')
    print('10 Most Significant Weights (Avg. of all KFold model weights):')
    print('--------------------------------------------------------------')
    for _, i in top10:
        print(dataset.get_feature_name(i), weights[i])


if __name__ == '__main__':
    main()


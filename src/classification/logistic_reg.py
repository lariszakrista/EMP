import argparse
import heapq

import numpy as np

from image_data import ImageDataKFold
from utils import get_lr


def print_header(h):
    bar = ''.join('-' for _ in range(len(h) + 1))
    print('\n{bar}\n{title}:\n{bar}'.format(bar=bar, title=h))


def print_results(acc, false_pos_ratio, accept_ratio, title):
    print_header(title)
    print('\tAccuracy:             {}'.format(acc))
    print('\tFalse positive ratio: {}'.format(false_pos_ratio))
    print('\tAcceptance ratio:     {}'.format(accept_ratio))


def average_weights_and_biases(w, b):
    return np.average(w, axis=0), np.average(b, axis=0)


def get_most_significant_weight_idx(weights, num=10):
    abs_weights = [[abs(i) for i in w] for w in weights]
    items = ((sum(abs_weights[i]), i) for i in range(len(abs_weights)))
    return heapq.nlargest(num, items, key=lambda x: x[0])


def evaluate_predictions(y_true, y_pred, pred_thresh, title='Model performance'):
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

    print_results(acc, false_pos_ratio, accept_ratio, title)

    return acc, false_pos_ratio, accept_ratio


def train_and_evaluate(dataset, pred_thresh=None):
    in_dim, out_dim = dataset.get_dim()

    results = list()
    weights, biases = list(), list()
    for train, test in dataset.get_folds():

        x_train, y_train = train
        x_test, y_test = test

        # Build and train model
        model = get_lr(in_dim, out_dim)
        model.fit(x_train, y_train, nb_epoch=10)

        # Save weights
        w, b = model.layers[0].get_weights()
        weights.append(w)
        biases.append(b)

        # Test model
        y_pred = model.predict(x_test)
        res = evaluate_predictions(y_test, y_pred, pred_thresh)

        results.append(res)

    acc, false_pos_ratio, accept_ratio = np.average(results, axis=0)

    print_results(acc, false_pos_ratio, accept_ratio, 'Average k-fold test case performance')

    # Average weights across k training iterations
    weights, biases = average_weights_and_biases(weights, biases)

    # Run averaged model on all images
    model = get_lr(in_dim, out_dim)
    model.layers[0].set_weights((weights, biases))
    x_test, y_test = dataset.get_all()
    y_pred = model.predict(x_test)
    evaluate_predictions(y_test, y_pred, pred_thresh, title='Results for averaged model on all images')

    return model


def main():
    parser = argparse.ArgumentParser(description='Totality image classifier')
    parser.add_argument('--pred-type', type=str, default='onehot')
    parser.add_argument('--pred-thresh', type=float, default=None)
    parser.add_argument('--labeled-data', type=str, default='labeled_data.json')
    parser.add_argument('--labels', type=str, default='labels.json')
    args = parser.parse_args()

    # Get data
    dataset = ImageDataKFold(nfolds=10, one_hot=(args.pred_type == 'onehot'),
                             labels_file=args.labels, labeled_data_file=args.labeled_data)

    # Train / evaluate / return model
    model = train_and_evaluate(dataset, args.pred_thresh)
 
    # Get weights
    weights, _ = model.layers[0].get_weights()

    # Print most significant weights
    top10 = get_most_significant_weight_idx(weights, 10)
    print_header('10 most significant weights (avg. of all k-fold model weights)')
    for _, i in top10:
        print(dataset.get_feature_name(i), weights[i])


if __name__ == '__main__':
    main()


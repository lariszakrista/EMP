import json
from random import shuffle

import numpy as np
from sklearn.model_selection import StratifiedKFold


class ImageDataBase(object):

    LABELS_FILE = 'labels.json'

    LABELED_DATA_FILE = 'labeled_data.json'

    def __init__(self, one_hot=True):
        self.one_hot = one_hot

        # Labels and their corresponding indices
        self.labels = json.loads(open(self.LABELS_FILE).read())

        # Load data and record number of training examples
        self.data = json.loads(open(self.LABELED_DATA_FILE).read())

    def get_feature_name(self, idx):
        for k, v in self.labels.items():
            if v == idx:
                return k
        raise KeyError

    def get_dataset(self, set_keys):
        xs = []
        ys = []

        for k in set_keys:
            feature_vec, y_val = self._get_feature_vector_and_label(k)
            xs.append(feature_vec)
            ys.append(y_val)

        return np.array(xs), np.array(ys)

    def get_dim(self):
        in_dim = len(self.labels)
        out_dim = 2 if self.one_hot else 1
        return in_dim, out_dim

    def _get_feature_vector_and_label(self, key):
        feature_vec = np.zeros(len(self.labels))

        for l in self.data[key]['labels']:
            feature_idx = self.labels[l[0]]
            feature_vec[feature_idx] = l[1]

        totality = (self.data[key]['classification'] == 'TOTALITY')
        if self.one_hot:
            y_val = [int(v) for v in (totality, not totality)]
        else:
            y_val = int(totality)

        return feature_vec, y_val


class ImageDataSimpleSplit(ImageDataBase):

    def __init__(self, one_hot=True, train_ratio=0.7):
        super().__init__(one_hot)

        num_train = int(len(self.data) * train_ratio)

        # Shuffle keys so that data is dispersed among train/test sets
        keys = list(self.data.keys())
        shuffle(keys)

        # Choose training/test examples
        self.train_keys = keys[:num_train]
        self.test_keys = keys[num_train:]

    def get_train(self):
        return self.get_dataset(self.train_keys)

    def get_test(self):
        return self.get_dataset(self.test_keys)


class ImageDataKFold(ImageDataBase):

    def __init__(self, nfolds, one_hot=True):
        super().__init__(one_hot)

        # Convert entire dataset into feature vectors and 
        # y labels
        self.xs, self.ys = self.get_dataset(self.data.keys())

        skf = StratifiedKFold(nfolds, shuffle=True)

        # split likes Y parameter (param 2) to have shape
        # (n_samples, )
        self.folds = skf.split(self.xs, [item[0] for item in self.ys])

    def get_all(self):
        return self.xs, self.ys

    def get_folds(self):
        """
        Generator returning k folds
        """
        while True:
            # StratifiedKFold.split returns a generator
            # Get the next set of indices from the generator
            train_idx, test_idx = next(self.folds)

            # Get feature vectors and y labels
            res = list()
            for idx in (train_idx, test_idx):
                xs = [self.xs[i] for i in idx]
                ys = [self.ys[i] for i in idx]

                res.append((np.array(xs), np.array(ys)))

            yield(res)


import json
import os
from random import shuffle

import cv2
import numpy as np
from sklearn.model_selection import StratifiedKFold


class ImageDataBase(object):

    TOTALITY_CLS_NAME = 'TOTALITY'
    NON_TOTALITY_CLS_NAME = 'NON_TOTALITY'

    def __init__(self, one_hot=True, labels_file='labels.json', labeled_data_file='labeled_data.json'):
        self.one_hot = one_hot

        # Labels and their corresponding indices
        self.labels = json.loads(open(labels_file).read())

        # Load data and record number of training examples
        self.data = json.loads(open(labeled_data_file).read())

    def get_feature_name(self, idx):
        for k, v in self.labels.items():
            if v == idx:
                return k
        raise KeyError

    def get_dataset(self, set_keys):
        xs = []
        ys = []

        for k in set_keys:
            try:
                x, y = self._get_xy(k)
                xs.append(x)
                ys.append(y)
            except Exception as e:
                print('Error obtaining x or y value. Skipping. Error: {}'.format(e))
                pass

        return np.array(xs), np.array(ys)

    @classmethod
    def get_class_name(cls, y):
        try:
            totality = y[0] == 1
        except IndexError:
            totality = y
        return cls.TOTALITY_CLS_NAME if totality else cls.NON_TOTALITY_CLS_NAME

    def get_dim(self):
        return self._get_in_dim(), self._get_out_dim()

    def _get_in_dim(self):
        return len(self.labels)

    def _get_out_dim(self):
        if self.one_hot:
            return 2
        else:
            return 1

    def _get_xy(self, key):
        return self._get_x(key), self._get_y(key)

    def _get_x(self, key):
        feature_vec = np.zeros(len(self.labels))

        for l in self.data[key]['labels']:
            feature_idx = self.labels[l[0]]
            feature_vec[feature_idx] = l[1]

        return feature_vec

    def _get_y(self, key):
        totality = (self.data[key]['classification'] == self.TOTALITY_CLS_NAME)
        if self.one_hot:
            y = [int(v) for v in (totality, not totality)]
        else:
            y = int(totality)
        return y

class ImageDataSimpleSplit(ImageDataBase):

    def __init__(self, train_ratio=0.7, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def __init__(self, nfolds, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

            yield res


class ImageDataNP(ImageDataSimpleSplit):

    IMG_DIM = (224, 224, 3)

    def __init__(self, img_dir, squash=False, **kwargs):
        super().__init__(**kwargs)

        self.img_dir = img_dir
        self.squash = squash

    def _get_in_dim(self):
        return self.IMG_DIM

    def _get_x(self, key):
        fpath = os.path.join(self.img_dir, os.path.basename(key))
        return self._open_img(fpath)

    def _open_img(self, fpath):
        print('Opening {}'.format(os.path.basename(fpath)))
        img = cv2.imread(fpath, cv2.IMREAD_COLOR)
        if img is None:
            raise cv2.error('Failed to open {}'.format(os.path.basename(fpath)))

        if not self.squash:
            sq_dim = min(img.shape[0], img.shape[1])
            yshift = int((img.shape[0] - sq_dim) / 2)
            xshift = int((img.shape[1] - sq_dim) / 2)

            yadd = img.shape[0] - (2 * sq_dim)
            xadd = img.shape[1] - (2 * sq_dim)

            img = img[yshift:(img.shape[0] - yshift - yadd), xshift:(img.shape[1] - xshift - xadd)]

        return cv2.resize(img, self.IMG_DIM[:2])


class PredictionWriter(object):
    def __init__(self):
        self.predictions = dict()

    def add(self, key, pred, y):
        v = {
            'labels': pred,
            'classification': ImageDataBase.get_class_name(y)
        }
        self.predictions[key] = v

    def commit(self, fpath):
        with open(fpath, 'w') as f:
            f.write(json.dumps(self.predictions))


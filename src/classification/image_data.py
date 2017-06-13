import json
import os
from random import shuffle

import cv2
import numpy as np
from sklearn.model_selection import StratifiedKFold

import constants as const
import utils


def _open_single_image(path, squash, dim):
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise cv2.error('Failed to open {}'.format(os.path.basename(fpath)))

    if not squash:
        sq_dim = min(img.shape[0], img.shape[1])

        yshift = int((img.shape[0] - sq_dim) / 2)
        xshift = int((img.shape[1] - sq_dim) / 2)

        yadd = img.shape[0] - (2 * sq_dim)
        xadd = img.shape[1] - (2 * sq_dim)

        img = img[yshift:(img.shape[0] - yshift - yadd), xshift:(img.shape[1] - xshift - xadd)]

    return cv2.resize(img, dim)


def _open_images(img_paths, squash, dim):
    images = list()
    for path in img_paths:
        images.append(_open_single_image(path, squash, dim))
    return images


class ImageDataBase(object):

    def __init__(self, one_hot=True, labels_file=None, labeled_data_file=None):
        self.one_hot = one_hot
        self.labels = None
        self.data = None

        # Labels and their corresponding indices
        if labels_file is not None:
            with open(labels_file) as f:
                self.labels = json.load(f)

        # Load data and record number of training examples
        if labeled_data_file is not None:
            with open(labeled_data_file) as f:
                self.data = json.load(f)

    def get_feature_name(self, idx):
        if self.labels is None:
            raise ValueError('Dataset features are unnamed')

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

    @staticmethod
    def get_class_name(y):
        try:
            return utils.decode_totality_prediction(y)
        except IndexError:
            return const.TOTALITY if y else const.NON_TOTALITY

    def get_dim(self):
        return self._get_in_dim(), self._get_out_dim()

    def _get_in_dim(self):
        if self.labels is None:
            raise ValueError('Input dimension not set')

        return len(self.labels)

    def _get_out_dim(self):
        if self.one_hot:
            return 2
        else:
            return 1

    def _get_xy(self, key):
        return self._get_x(key), self._get_y(key)

    def _get_x(self, key):
        """
        Assumens self.labels is set. Otherwise will raise an exception. If using a subclass
        that does not use self.labels, this method should be overridden.
        """
        feature_vec = np.zeros(len(self.labels))

        for l in self.data[key]['labels']:
            feature_idx = self.labels[l[0]]
            feature_vec[feature_idx] = l[1]

        return feature_vec

    def _get_y(self, key):
        totality = (self.data[key]['classification'] == const.TOTALITY)
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

    def __init__(self, nfolds, custom_data=None, **kwargs):
        super().__init__(**kwargs)

        if custom_data is not None:
            self.xs, self.ys = custom_data

        else:
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

    def _get_in_dim(self):
        return self.xs[0].shape[0]


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
        return _open_single_image(fpath, self.squash, self.IMG_DIM[:2])


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


class ImageSet(object):

    def __init__(self, img_paths, squash=True, dim = (224, 224)):
        self.img_paths = img_paths
        self.squash = squash
        self.dim = dim

    def get_batches(self, batch_size=32):
        start = 0
        end = min(batch_size, len(self.img_paths))

        while start < len(self.img_paths):
            images = _open_images(self.img_paths[start:end], self.squash, self.dim)
            yield images, start, end
            start = end
            end = min(end + batch_size, len(self.img_paths))

        raise StopIteration

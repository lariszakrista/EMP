import os
import subprocess

from keras.applications.vgg16 import VGG16
from keras.applications.vgg19 import VGG19
from keras.layers import Dense
from keras.models import Sequential

import constants


def decode_totality_prediction(pred):
    if pred[0] > pred[1]:
        return constants.TOTALITY
    else:
        return constants.NON_TOTALITY


def download_images(img_dir, img_uris):
    """
    Downloads images to <img_dir>/images.txt.
    img_uris is a list of Google Cloud Storage uris.
    """
    if not os.path.isdir(img_dir):
        os.mkdir(img_dir)

    with open(os.path.join(img_dir, 'images.txt'), 'w+') as f:
        f.write('\n'.join(img_uris))
        f.seek(0)
        subprocess.run(['gsutil', '-m', 'cp', '-I', img_dir], stdin=f)


def get_vgg(name, include_top=True, weights=None, classes=2):
    """
    Returns VGG16/19 model, (depending on cls parameter)
    """
    if name == 'VGG16':
        cls = VGG16
    elif name == 'VGG19':
        cls = VGG19

    model = cls(include_top=include_top, input_shape=(224, 224, 3), weights=weights, classes=classes)
    model.compile(loss='mse', optimizer='rmsprop')

    return model


def get_lr(in_dim, out_dim):
    """
    Returns simple one layer logistic regression model
    """
    model = Sequential()
    model.add(Dense(out_dim, input_dim=in_dim))
    model.compile(optimizer='rmsprop', loss='mse', metrics=['accuracy'])
    return model

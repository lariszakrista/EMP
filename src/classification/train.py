import argparse
import json

import numpy as np
from keras import backend as K

from image_data import ImageDataKFold
from image_data import ImageDataNP
from logistic_reg import train_and_evaluate as train_and_eval_lr
from utils import download_images
from utils import get_vgg


def main():
    parser = argparse.ArgumentParser(description='A test')
    parser.add_argument('--download', default=False, action='store_true')
    parser.add_argument('--img-dir', type=str, default='img')
    parser.add_argument('--label-file', type=str, default='labeled_data.json')
    parser.add_argument('--save', type=str, default=None)
    args = parser.parse_args()

    if args.download:
        with open(args.label_file) as f:
            download_images(args.img_dir, list(json.load(f).keys()))

    # VGG Phase
    print('Collecting dataset...')
    dataset = ImageDataNP(args.img_dir, labeled_data_file=args.label_file, train_ratio=1.0, squash=True)
    x_train, y_train = dataset.get_train()

    vgg = get_vgg('VGG19', weights='imagenet', classes=1000)
    inp = vgg.input
    out = vgg.get_layer(name='fc2').output
    functor = K.function([inp], [out])

    vgg_relu_out = list()
    batch_size=32
    start, end = 0, 0
    print('Classifying images...')
    for i in range(int((x_train.shape[0] + batch_size - 1) / batch_size)):
        end = min((i + 1) * batch_size, x_train.shape[0])
        print('Batch {}, images[{}:{}]'.format(i, start, end))

        vecs = functor([x_train[start:end]])
        vgg_relu_out.extend(vecs[0])

        # Update start index
        start = end

    # Logistic Regression Phase
    kfold_dataset = ImageDataKFold(nfolds=10, custom_data=(np.array(vgg_relu_out), y_train))
    model = train_and_eval_lr(kfold_dataset)

    # Save model?
    if args.save is not None:
        model.save(args.save)


if __name__ == '__main__':
    main()


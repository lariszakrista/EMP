import argparse
import json
import os

from keras import backend as K
from keras.models import load_model
import numpy as np

from image_data import ImageSet
from utils import decode_totality_prediction
from utils import download_images
from utils import get_vgg


def main():
    parser = argparse.ArgumentParser(description='Totality image classifier')
    parser.add_argument('--download', default=False, action='store_true')
    parser.add_argument('--img-dir', type=str, default='img')
    parser.add_argument('--img-uri', type=str, default='img/img.txt')
    parser.add_argument('--lr-model', type=str, default='lr_model.h5')
    parser.add_argument('--save', type=str, default=None)
    args = parser.parse_args()

    # Create URI list
    with open(args.img_uri) as f:
        img_uri = [l.strip() for l in f.readlines()]

    if args.download:
        download_images(args.img_dir, img_uri)

    # Create list of paths to local image files
    img_paths = [os.path.join(args.img_dir, os.path.basename(i)) for i in img_uri]

    # ImageSet object will provide images in for loop below.
    # This object provides a generator to access batches of
    # images, allowing only one batch to be loaded into RAM
    # at a time.
    images = ImageSet(img_paths)

    # Create VGG19 model
    vgg = get_vgg('VGG19', weights='imagenet', classes=1000)
    inp = vgg.input
    out = vgg.get_layer(name='fc2').output
    functor = K.function([inp], [out])

    print('Classifying images...')
    vgg_fc2_out = list()
    batch_size = 32
    i = 0
    for batch, start, end in images.get_batches(batch_size):
        print('Batch {}, images[{}:{}]'.format(i, start, end))
        vecs = functor([batch])
        vgg_fc2_out.extend(vecs[0])
        i += 1

    # Load trained logistic regression model
    model = load_model(args.lr_model)

    # Classify tensors from VGG19 using LR model
    predictions = model.predict(np.array(vgg_fc2_out))

    # Prediction dictionary. Used if the --save argument is supplied
    pred_dict = dict()

    # Print predictions and assemble pred_dict
    for i in range(len(img_uri)):
        cur_img_uri = img_uri[i]
        cls_name = decode_totality_prediction(predictions[i])

        pred_dict[cur_img_uri] = cls_name
        print(cur_img_uri, cls_name)

    # Save predictions?
    if args.save is not None:
        with open(args.save, 'w') as f:
            json.dump(pred_dict, f)


if __name__ == '__main__':
    main()


import argparse
import json

from keras.applications.imagenet_utils import decode_predictions
from keras.preprocessing.image import ImageDataGenerator

from image_data import ImageDataNP
from image_data import PredictionWriter
from utils import download_images
from utils import get_vgg


def get_trained_model(x_train, y_train):
    """
    Returns VGG19 model trained on x_train, y_train
    """
    model = get_vgg('VGG19')

    datagen = ImageDataGenerator(
        featurewise_center=False,           # set input mean to 0 over the dataset
        samplewise_center=False,            # set each sample mean to 0
        featurewise_std_normalization=True, # divide inputs by std of the dataset
        samplewise_std_normalization=False, # divide each input by its std
        zca_whitening=False,                # apply ZCA whitening
        rotation_range=180,                 # randomly rotate images in the range (degrees, 0 to 180)
        width_shift_range=0.2,              # randomly shift images horizontally (fraction of total width)
        height_shift_range=0.2,             # randomly shift images vertically (fraction of total height)
        horizontal_flip=True,               # randomly flip images
        vertical_flip=True)                 # randomly flip images
    datagen.fit(x_train)

    batch_size = 32
    n_epochs = 10
    n_iters = int(x_train.shape[0] * n_epochs / 32)

    i = 0
    for x_batch, y_batch in datagen.flow(x_train, y_train, batch_size=32):
        loss = model.train_on_batch(x_batch, y_batch)
        print('training complete for batch {}. loss: {}'.format(i, loss))
        i += 1

        if i == n_iters:
            break

    return model


def record_batch_results(writer, preds, y, key_set, start):
    """
    Utility function to record imagenet predictions.
    Prints results to screen, adds to PredictionWriter writer.
    """
    results = decode_predictions(preds, top=10)

    i = 0
    for res in results:
        key = key_set[start + i]
        p = [[str(r[1]), float(r[2])] for r in res]
        writer.add(key, p, y[i])

        print('{}: {}'.format(key, y[i]))
        print(p)
        print()
        i += 1


def main():
    parser = argparse.ArgumentParser(description='Totality image classifier using VGG in Keras')
    parser.add_argument('--download', default=False, action='store_true')
    parser.add_argument('--img-dir', type=str, default='img')
    parser.add_argument('--label-file', type=str, default='labeled_data.json')
    parser.add_argument('--output-file', type=str, default='vgg_output_labels.json')
    args = parser.parse_args()

    if args.download:
        with open(args.label_file) as f:
            download_images(args.img_dir, list(json.load(f).keys()))

    print('Collecting dataset...')
    dataset = ImageDataNP(args.img_dir, labeled_data_file=args.label_file, train_ratio=1.0, squash=True)
    x_train, y_train = dataset.get_train()

    model = get_vgg('VGG16', weights='imagenet', classes=1000)

    writer = PredictionWriter()
    batch_size=32
    start, end = 0, 0
    print('Classifying images...')
    for i in range(int((x_train.shape[0] + batch_size - 1) / batch_size)):
        end = min((i + 1) * batch_size, x_train.shape[0])
        print('Batch {}, images[{}:{}]'.format(i, start, end))

        # Obtain predictions and print results
        preds = model.predict(x_train[start:end])
        record_batch_results(writer, preds, y_train[start:end], dataset.train_keys, start)

        # Update start index
        start = end

    writer.commit(args.output_file)


if __name__ == '__main__':
    main()


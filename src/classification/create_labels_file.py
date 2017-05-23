"""
Simple script to create labels file needed by image_data.ImageData
from the output of /tools/label_images.
"""

import json

from image_data import ImageData


def main():
    data = json.loads(open(ImageData.LABELED_DATA_FILE).read())
    labels = dict()

    i = 0
    for k in data:
        for l in data[k]['labels']:
            if l[0] not in labels:
                labels[l[0]] = i
                i += 1

    open(ImageData.LABELS_FILE, 'w').write(json.dumps(labels))


if __name__ == '__main__':
    main()


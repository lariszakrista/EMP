"""
Simple script to create labels file needed by image_data.ImageData
from the output of /tools/label_images.
"""
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description='Totality image classifier')
    parser.add_argument('--labeled-data', type=str, default='labeled_data.json')
    parser.add_argument('--labels', type=str, default='labels.json')
    args = parser.parse_args()

    data = json.loads(open(args.labeled_data).read())
    labels = dict()

    i = 0
    for k in data:
        for l in data[k]['labels']:
            if l[0] not in labels:
                labels[l[0]] = i
                i += 1

    open(args.labels, 'w').write(json.dumps(labels))


if __name__ == '__main__':
    main()


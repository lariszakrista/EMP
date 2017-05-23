import argparse
import json
from multiprocessing import Pool
from time import sleep

from google.cloud import vision

from keys import service_account_file


def label(batch):
    client = vision.Client.from_service_account_json(service_account_file)
    results = dict()

    i = 0
    while i < len(batch):
        uri, classification = batch[i]
        print('Labeling {}...'.format(uri))

        # Requests can fail due to insufficient quota. Cloud Vision quota
        # is allocated as # requests / 100 seconds, so if requests fail,
        # we try again after sleeping for 100 seconds.
        #
        # TODO make this check that the error that occured is in fact due
        # to insufficient quota, otherwise this loop could run forever.
        try:
            img = client.image(source_uri=uri)
            labels = img.detect_labels()

        except Exception as e:
            print('Error occured detecting labels for {}:'.format(uri))
            print(e)
            print('Sleeping for 100 seconds...')
            sleep(100)
            continue

        results[uri] = dict()
        results[uri]['labels'] = [(l.description, l.score) for l in labels]
        results[uri]['classification'] = classification
        i += 1

    return results


def label_all(uri_file):
    items = [l.strip().split() for l in open(uri_file).readlines()]
    batch = list()

    for i in range(0, len(items), 4):
      batch.append(items[i:i+4])

    p = Pool(20)
    res_dicts = p.map(label, batch)

    res = dict()
    for d in res_dicts:
        res.update(d)

    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Classifies given image.')
    parser.add_argument('--uri_file', default='gs_files.txt')
    parser.add_argument('--out_file', default='labeled_data.json')
    args = parser.parse_args()
    
    results = label_all(args.uri_file)

    with open(args.out_file, 'w') as f:
        f.write(json.dumps(results))

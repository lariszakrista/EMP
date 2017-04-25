import datetime
from getpass import getuser
import os
import subprocess


GCS_URL_FMT = 'https://storage.googleapis.com/{}/{}'


def current_git_hash_str():
    return subprocess.check_output('git rev-parse --short HEAD', shell=True).decode('utf-8').strip()


def gcs_url(fname, bucket):
    return GCS_URL_FMT.format(bucket, fname)


class FilenameConverter(object):

    def __init__(self):
        self.mappings = dict()
        self.datetime = datetime.datetime.now()
        self.time_str = self.datetime.strftime('%Y_%m_%d-%H_%M_%S')
        self.git_hash = current_git_hash_str()
        self.user = getuser()

    def get_run_specific_filename(self, current_filename):
        # Just in case
        current_filename = os.path.basename(current_filename)

        # Extract file extension
        name, ext = os.path.splitext(current_filename)

        # Assemble run specific filename
        name = '-'.join((name, self.git_hash, self.user, self.time_str))
        new_fname = name + ext

        # Save old -> new filename mapping
        self.mappings[current_filename] = new_fname

        return new_fname

    def commit(self, dir_path):
        for f in self.mappings:
            old = os.path.join(dir_path, f)
            new = os.path.join(dir_path, self.mappings[f])
            os.rename(old, new)


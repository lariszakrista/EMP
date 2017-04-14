import subprocess

def current_git_hash_str():
    return subprocess.check_output('git rev-parse HEAD', shell=True).decode('utf-8').strip()


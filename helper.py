import json
import os
import pickle
import sys


def session(jsn: str, filename: str):
    if jsn is None or filename is None:
        exit(f'usage: python {sys.argv[0]} session session_json session_file')

    session = json.loads(jsn)
    with open(filename, 'wb') as sessionfile:
        os.chmod(filename, 0o600)
        pickle.dump(session, sessionfile)


def convert_session(filename: str):
    file_name, ext = os.path.splitext(filename)
    assert ext == '.json', 'Expecting json file'

    session = json.loads(open(filename, 'r').read())

    with open(file_name, 'wb') as sessionfile:
        os.chmod(file_name, 0o600)
        pickle.dump(session, sessionfile)


def print_session(filename: str):
    with open(filename, 'rb') as sessionfile:
        print(json.dumps(pickle.load(sessionfile)))


if __name__ == '__main__':
    if len(sys.argv) > 1:
        func = locals()[sys.argv[1]] if sys.argv[1] in locals() else sys.argv[1]
        if callable(func):
            print(f'Invoking {func.__name__}()')
            func(*sys.argv[2:])
        else:
            print('{} is not callable'.format(func))

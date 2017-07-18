import os
import errno


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as e:  # Python >2.5
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise e

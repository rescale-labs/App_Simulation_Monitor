import glob
import os
import sys


def is_debug():
    """
    Checks whether code is executed with debugger
    """
    gettrace = getattr(sys, "gettrace", None)

    if gettrace is None:
        return False
    else:
        v = gettrace()
        if v is None:
            return False
        else:
            return True


def find_file(file_glob, root_dir):
    files = glob.glob(file_glob, recursive=True, root_dir=root_dir)
    return os.path.join(root_dir, files[0]) if files else None

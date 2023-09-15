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

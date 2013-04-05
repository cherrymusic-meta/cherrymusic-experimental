import sys


def get(name):
    qualname = __qualify_module(name)
    try:
        return sys.modules[qualname]
    except KeyError:
        try:
            return __import_module(qualname)
        except ImportError as e:
            print(e)
            raise LookupError(name)


def __import_module(qualname):
    __import__(qualname)
    return sys.modules[qualname]


def __qualify_module(name):
    return '.'.join((__package__, name))

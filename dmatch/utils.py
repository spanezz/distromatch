import textwrap
import tempfile
import os.path

# From http://code.activestate.com/recipes/363602-lazy-property-evaluation/
class lazy_property(object):
    """
    Lazily evaluated const member
    """
    def __init__(self, calculate_function):
        self._calculate = calculate_function

    def __get__(self, obj, _=None):
        if obj is None:
            return self
        value = self._calculate(obj)
        setattr(obj, self._calculate.func_name, value)
        return value

class atomic_writer(object):
    """
    Atomically write to a file
    """
    def __init__(self, fname, mode=0664):
        self.fname = fname
        self.mode = mode
        dirname = os.path.dirname(self.fname)
        self.outfd = tempfile.NamedTemporaryFile(dir=dirname)

    def __enter__(self):
        return self.outfd

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.outfd.flush()
            os.fsync(self.outfd.fileno())
            os.fchmod(self.outfd.fileno(), self.mode)
            os.rename(self.outfd.name, self.fname)
            self.outfd.delete = False
        self.outfd.close()
        return False

def splitdesc(text):
    if text is None:
        return "", ""
    desc = text.split("\n", 1)
    if len(desc) == 2:
        return desc[0], textwrap.dedent(desc[1])
    else:
        return desc[0], ""

def tags_to_facets(seq):
    """
    Convert a sequence of tags into a sequence of facets.

    Note that no attempt is made to remove duplicates from the facet sequence.
    """
    for t in seq:
        yield t.split("::")[0]

class Sequence(object):
    def __init__(self):
        self.val = 0
    def next(self):
        self.val += 1
        return self.val


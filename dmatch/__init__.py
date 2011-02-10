from rules import *

try:
    from distro import *
    from matcher import *
    HAVE_ENGINE=True
except ImportError, e:
    HAVE_ENGINE=False
    MISSING_ENGINE_REASON=str(e)

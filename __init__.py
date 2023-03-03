try:
    from . import config
except ModuleNotFoundError:
    pass
try:
    from . import convert_to_SI
except ModuleNotFoundError:
    pass
#from . import DFS_AIP
try:
    from . import dropbox
except ModuleNotFoundError:
    pass
try:
    from . import exceptions
except ModuleNotFoundError:
    pass
try:
    from . import fstr
except ModuleNotFoundError:
    pass
try:
    from . import log
except ModuleNotFoundError:
    pass
try:
    from . import math
except ModuleNotFoundError:
    pass
try:
    from . import media
except ModuleNotFoundError:
    pass


__all__=[
    "config",
    "convert_to_SI",
    #DFS_AIP,
    "dropbox",
    "exceptions",
    "fstr",
    "log",
    "math",
    "media"
]
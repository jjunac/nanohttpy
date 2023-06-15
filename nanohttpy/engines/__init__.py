from typing import TYPE_CHECKING

from nanohttpy.lazy_loader import LazyLoader as _LazyLoader

if TYPE_CHECKING:
    from nanohttpy.engines.python import PythonEngine
    from nanohttpy.engines.uvloop import UvloopEngine

_engines_package = "nanohttpy.engines."

_python = _LazyLoader("_python", globals(), _engines_package + "python")
_uvloop = _LazyLoader("_uvloop", globals(), _engines_package + "uvloop")

# TODO: try to automate this part a bit

def __getattr__(name):
    if name in ['PythonEngine']:
        return _python.PythonEngine
    elif name in ['UvloopEngine']:
        return _uvloop.UvloopEngine
    else:
        raise AttributeError(f'module {__name__} doesn\'t have attribute {name}')

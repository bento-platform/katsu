#!/usr/bin/env python3

import importlib.metadata

from . import metadata
from . import patients


__all__ = [
    "name",
    "__version__",
    "metadata",
    "patients",
]

name = __package__
__version__ = importlib.metadata.version(__package__)

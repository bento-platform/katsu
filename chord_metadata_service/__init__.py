#!/usr/bin/env python3

import os

from chord_lib.utils import get_own_version
from pathlib import Path

from . import metadata
from . import patients

name = "chord_metadata_service"
__version__ = get_own_version(os.path.join(Path(os.path.dirname(os.path.realpath(__file__))).parent, "setup.py"), name)
__all__ = ["name", "__version__", "metadata", "patients"]

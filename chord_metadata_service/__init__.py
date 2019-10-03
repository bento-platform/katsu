#!/usr/bin/env python3

import os
import re

from pathlib import Path
from pkg_resources import get_distribution, DistributionNotFound

from . import metadata
from . import patients

name = "chord_metadata_service"

try:
    __version__ = get_distribution(name).version
except DistributionNotFound:
    setup_path = os.path.join(Path(os.path.dirname(os.path.realpath(__file__))).parent, "setup.py")
    __version__ = [re.search(r"(\d+\.\d+\.\d+)", l).group(1) for l in open(setup_path, "r").readlines()
                   if "    version" in l][0]

__all__ = ["name", "__version__", "metadata", "patients"]

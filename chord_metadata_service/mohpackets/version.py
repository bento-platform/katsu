import datetime
import functools
import os
import subprocess
import sys

from django.utils.regex_helper import _lazy_re_compile

# these functions provide utilities for managing version numbers
# generating PEP 440-compliant version strings
# and retrieving git changeset information.


def get_version(version=None):
    """
    Return a PEP 440-compliant version number from the given version tuple.

    Args:
        version (tuple, optional): Version tuple in the form (X, Y, Z, release, N).
            Defaults to None.

    Returns:
        str: PEP 440-compliant version number.

    Versioning Stages:
        - Dev: work in progress during active development.
        - Alpha: early releases with major features but known issues and missing functionality.
        - Beta: stable releases requiring wider testing, although some bugs may still exist.
        - RC: feature-complete and stable releases pending user testing and feedback.
        - Final: stable releases ready for production.

    Examples:
        >>> VERSION = (1, 0, 0, "alpha", 0)
        >>> get_version(VERSION)
        '1.0.0.dev<git_hash>'

        >>> alpha_version = (2, 0, 0, "alpha", 1)
        >>> get_version(alpha_version)
        '2.0.0a1'

        >>> beta_version = (3, 0, 0, "beta", 2)
        >>> get_version(beta_version)
        '3.0.0b2'

        >>> rc_version = (4, 0, 0, "rc", 3)
        >>> get_version(rc_version)
        '4.0.0rc3'

        >>> final_version = (1, 2, 3, "final", 0)
        >>> get_version(final_version)
        '1.2.3'
    """

    version = get_complete_version(version)

    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|rc}N - for alpha, beta, and rc releases

    main = get_main_version(version)

    sub = ""
    if version[3] == "alpha" and version[4] == 0:
        git_changeset = get_git_changeset()
        if git_changeset:
            sub = ".dev%s" % git_changeset

    elif version[3] != "final":
        mapping = {"alpha": "a", "beta": "b", "rc": "rc"}
        sub = mapping[version[3]] + str(version[4])

    return main + sub


def get_main_version(version=None):
    """Return main version (X.Y[.Z]) from VERSION."""
    version = get_complete_version(version)
    parts = 2 if version[2] == 0 else 3
    return ".".join(str(x) for x in version[:parts])


def get_complete_version(version=None):
    """
    Return a tuple of the django version. If version argument is non-empty,
    check for correctness of the tuple provided.
    """
    if version is None:
        from django import VERSION as version
    else:
        assert len(version) == 5
        assert version[3] in ("alpha", "beta", "rc", "final")

    return version


def get_docs_version(version=None):
    version = get_complete_version(version)
    if version[3] != "final":
        return "dev"
    else:
        return "%d.%d" % version[:2]


@functools.lru_cache
def get_git_changeset():
    """Return a numeric identifier of the latest git changeset.

    The result is the UTC timestamp of the changeset in YYYYMMDDHHMMSS format.
    This value isn't guaranteed to be unique, but collisions are very unlikely,
    so it's sufficient for generating the development version numbers.
    """
    # Repository may not be found if __file__ is undefined, e.g. in a frozen
    # module.
    if "__file__" not in globals():
        return None
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_log = subprocess.run(
        "git log --pretty=format:%ct --quiet -1 HEAD",
        capture_output=True,
        shell=True,
        cwd=repo_dir,
        text=True,
    )
    timestamp = git_log.stdout
    tz = datetime.timezone.utc
    try:
        timestamp = datetime.datetime.fromtimestamp(int(timestamp), tz=tz)
    except ValueError:
        return None
    return timestamp.strftime("%Y%m%d%H%M%S")


def get_git_hash():
    """Return the git hash of the latest changeset."""
    # Repository may not be found if __file__ is undefined, e.g. in a frozen module.
    if "__file__" not in globals():
        return None
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    git_log = subprocess.run(
        "git rev-parse --short HEAD",
        capture_output=True,
        shell=True,
        cwd=repo_dir,
        text=True,
    )
    git_hash = git_log.stdout.strip()
    return git_hash


version_component_re = _lazy_re_compile(r"(\d+|[a-z]+|\.)")


def get_version_tuple(version):
    """
    Return a tuple of version numbers (e.g. (1, 2, 3)) from the version
    string (e.g. '1.2.3').
    """
    version_numbers = []
    for item in version_component_re.split(version):
        if item and item != ".":
            try:
                component = int(item)
            except ValueError:
                break
            else:
                version_numbers.append(component)
    return tuple(version_numbers)


VERSION = (1, 0, 0, "final", 0)
__version__ = get_version(VERSION)

import os
import subprocess

#####################################################
#                                                   #
#   CURRENT KATSU VERSION, MAKE CHANGE IF NEEDED    #
#                                                   #
#####################################################

# Format: major.minor.patch.status
VERSION = (2, 2, 0, "stable")


def get_version():
    """
    Returns a version number in a standard format

    Versioning Stages:
        - Dev: work in progress during active development.
        - Alpha: early releases with new features for testing
        - Beta: later releases, some bugs may still exist.
        - RC: stable releases pending user testing and feedback.
        - Stable: ready for production.

    Examples:
        >>> VERSION = (1, 0, 0, "dev")
        >>> get_version()
        '1.0.0.dev<git_hash>'

        >>> VERSION = (1, 0, 0, "alpha")
        >>> get_version()
        '1.0.0.a'

        >>> VERSION = (1, 0, 0, "beta")
        >>> get_version()
        '1.0.0.b'

        >>> VERSION = (1, 0, 0, "rc")
        >>> get_version()
        '1.0.0.rc'

        >>> VERSION = (1, 0, 0, "stable")
        >>> get_version()
        '1.0.0'
    """

    major, minor, patch, status = VERSION[:4]

    version_string = f"{major}.{minor}.{patch}"

    if status == "dev":
        git_hash = get_git_hash()
        version_string += f".dev.{git_hash}" if git_hash is not None else ".dev"
    elif status in ("alpha", "beta", "rc"):
        version_string += f".{status[0]}"
    elif status != "stable":
        return "Invalid version"

    return version_string


def get_git_hash():
    """Return the git hash of the latest changeset."""
    try:
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
    except Exception:
        return None


__version__ = get_version()

from .. import __version__
from .settings import BENTO_SERVICE_KIND, CHORD_SERVICE_TYPE, CHORD_SERVICE_ID, DEBUG
import subprocess
import os

path_for_git = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


def before_first_request_func():
    try:
        subprocess.run(["git", "config", "--global", "--add", "safe.directory", str(path_for_git)])
    except Exception as e:
        except_name = type(e).__name__
        print("Error in dev-mode retrieving git folder configuration", except_name)


before_first_request_func()

# Service info according to spec https://github.com/ga4gh-discovery/ga4gh-service-info

SERVICE_INFO = {
    "id": CHORD_SERVICE_ID,
    "name": "Katsu",  # TODO: Globally unique?
    "type": CHORD_SERVICE_TYPE,
    "environment": "prod",
    "description": "Clinical and phenotypic metadata service implementation based on Phenopackets schema.",
    "organization": {
        "name": "C3G",
        "url": "https://www.computationalgenomics.ca"
    },
    "contactUrl": "mailto:info@c3g.ca",
    "version": __version__,
    "bento": {
        "serviceKind": BENTO_SERVICE_KIND,
    },
}


def service_info_git():
    info = {
        **SERVICE_INFO,
        "environment": "dev",
    }
    try:
        if res_tag := subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"]):
            res_tag_str: str = res_tag.decode().rstrip()
            info["git_tag"] = res_tag_str
            info["bento"]["gitTag"] = res_tag_str
        if res_branch := subprocess.check_output(["git", "branch", "--show-current"]):
            res_branch_str: str = res_branch.decode().rstrip()
            info["git_branch"] = res_branch_str
            info["bento"]["gitBranch"] = res_branch_str

    except Exception as e:
        except_name = type(e).__name__
        print("Error in dev-mode retrieving git information", except_name)

    return info  # updated service info with the git info


if DEBUG:
    SERVICE_INFO = service_info_git()

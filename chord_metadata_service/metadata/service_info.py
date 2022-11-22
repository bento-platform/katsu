from .. import __version__
from .settings import CHORD_SERVICE_TYPE, CHORD_SERVICE_ID, DEBUG
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
    "name": "Metadata Service",  # TODO: Globally unique?
    "type": CHORD_SERVICE_TYPE,
    "environment": "prod",
    "description": "Metadata service implementation based on Phenopackets schema",
    "organization": {
        "name": "C3G",
        "url": "http://www.computationalgenomics.ca"
    },
    "contactUrl": "mailto:ksenia.zaytseva@mcgill.ca",
    "version": __version__
}

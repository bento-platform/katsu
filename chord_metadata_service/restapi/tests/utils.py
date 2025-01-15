import json
import inspect
import os


# Helper functions for tests


def load_local_json(file_name):
    """
    Helper function that can be used to load json files
    that are in the same directory as the caller.

    Caller dir is obtained from the call stack.
    Only a file_name value is required.
    """

    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    caller_path = os.path.dirname(module.__file__)
    file_path = os.path.join(caller_path, file_name)

    with open(file_path) as f:
        return json.load(f)

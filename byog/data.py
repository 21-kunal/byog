import os

GIT_DIR = ".byog"


def init(path: str):
    """Initilize a new, empty repository."""

    if os.path.isdir(os.path.join(path)):
        if not os.path.isdir(os.path.join(path, GIT_DIR)):
            #  TODO: Create directories and files for .byog
            os.makedirs(os.path.join(path, GIT_DIR))
        else:
            raise Exception(f'Directory is not empty. ".byog" is already present.')
    else:
        raise Exception(f'Given path "{path}" does not exists.')

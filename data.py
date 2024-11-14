import os
import hashlib

BYOG_DIR = ".byog"


def find_repo(path: str) -> str:
    path = os.path.realpath(path)

    if os.path.isdir(os.path.join(path, ".byog")):
        return path

    parent = os.path.realpath(os.path.join(path, ".."))

    if parent == path:
        raise Exception("No byog directory")

    return find_repo(parent)


def init(path: str) -> None:
    """Initilize a new, empty repository."""

    if os.path.isdir(os.path.join(path)):
        if not os.path.isdir(os.path.join(path, BYOG_DIR)):
            #  TODO: Create directories and files for .byog
            os.makedirs(os.path.join(path, BYOG_DIR))
            os.makedirs(os.path.join(path, BYOG_DIR, "objects"))
            realpath = os.path.realpath(os.path.join(path, BYOG_DIR))
            print(f"Initilized empty byog repository in {realpath}")
        else:
            raise Exception(f'Directory is not empty. ".byog" is already present.')
    else:
        raise Exception(f'Given path "{path}" does not exists.')


def hash_obj(path: str, type_: str = "blob") -> str:
    if os.path.isfile(os.path.realpath(path)):
        with open(path, "rb") as f:
            obj = type_.encode() + b"\x00" + f.read()
            obj_id = hashlib.sha1(obj).hexdigest()
            repo_path = find_repo(os.path.realpath(path))
            with open(f"{repo_path}/.byog/objects/{obj_id}", "wb") as ff:
                ff.write(obj)

            return obj_id
    else:
        raise Exception(f'Given file path "{path}" is not correct.')


def get_object(oid: str, expected: str = "blob") -> str:
    repo_path = find_repo(".")
    if os.path.isfile(os.path.join(repo_path, BYOG_DIR, "objects", oid)):
        path = os.path.join(repo_path, BYOG_DIR, "objects", oid)
        with open(path, "r") as f:
            obj = f.read()
            type_, _, data = obj.partition("\x00")

            if type_ != expected:
                raise Exception(f'Expected "{expected}", but got {type_}')

            return data
    else:
        raise Exception(f'Given Object ID "{oid}" does not exists.')

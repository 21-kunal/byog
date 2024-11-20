import os
import hashlib
from collections import namedtuple

BYOG_DIR = ".byog"

RefValue = namedtuple("RefValue", ["symbolic", "value"])

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
            os.makedirs(os.path.join(path, BYOG_DIR))
            os.makedirs(os.path.join(path, BYOG_DIR, "objects"))
            realpath = os.path.realpath(os.path.join(path, BYOG_DIR))
            print(f"Initilized empty byog repository in {realpath}")
        else:
            raise Exception(f'Directory is not empty. ".byog" is already present.')
    else:
        raise Exception(f'Given path "{path}" does not exists.')


def hash_obj(data: bytes, type_: str = "blob") -> str:
    obj = type_.encode() + b"\x00" + data
    obj_id = hashlib.sha1(obj).hexdigest()
    repo_path = find_repo(os.path.realpath("."))

    with open(f"{repo_path}/.byog/objects/{obj_id}", "wb") as f:
        f.write(obj)

    return obj_id


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


def update_ref(ref: str, value: RefValue, deref: bool = True) -> None:
    ref = _get_ref_internal(ref, deref)[0]

    assert value.value

    if value.symbolic:
        temp_value = f"ref: {value.value}"
    else:
        temp_value = value.value

    path = find_repo(".")
    path = f"{path}/{BYOG_DIR}/{ref}"

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(temp_value)


def get_ref(ref: str, deref: bool = True) -> RefValue:
    return _get_ref_internal(ref, deref)[1]

def _get_ref_internal(ref: str, deref: bool) -> tuple[str, RefValue]:
    path = find_repo(".")
    path = f"{path}/{BYOG_DIR}/{ref}"
    value = None

    if os.path.isfile(path):
        with open(path) as f:
            value = f.read().strip()

    symbolic = bool(value) and value.startswith("ref:")

    if symbolic:
        if deref:
            value = value.split(":",1)[1].strip()
            return _get_ref_internal(ref=value, deref=True)

    return ref, RefValue(symbolic=symbolic, value=value)

def iter_refs(deref: bool = True):
    refs=["HEAD"]
    path = find_repo(".")
    path = f"{path}/{BYOG_DIR}/refs/"
    for root, _, filenames in os.walk(path):
        root = os.path.relpath(root, BYOG_DIR)
        refs.extend(f"{root}/{name}"  for name in filenames)

    for refname in refs:
        yield refname, get_ref(refname, deref)


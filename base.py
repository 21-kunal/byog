import os
from collections import namedtuple
import data


Commit = namedtuple("commit", ["parent", "tree", "message"])


def write_tree(dir: str):
    entires = []
    with os.scandir(dir) as files:
        for file in files:
            if is_ignore(os.path.realpath(file.path)):
                continue
            if file.is_file(follow_symlinks=False):
                type_ = "blob"
                with open(os.path.realpath(file.path), "rb") as f:
                    oid = data.hash_obj(f.read())
            elif file.is_dir(follow_symlinks=False):
                type_ = "tree"
                oid = write_tree(os.path.realpath(file))

            entires.append((file.name, oid, type_))

    tree = "".join(f"{name} {oid} {type_}\n" for name, oid, type_ in sorted(entires))

    return data.hash_obj(tree.encode(), "tree")


def is_ignore(path: str):
    return ".byog" in path.split("/")


def _iter_tree_entries(oid: str):
    if not oid:
        return

    tree = data.get_object(oid, "tree")

    for entry in tree.splitlines():
        name, oid, type_ = entry.split(" ", 2)
        yield name, oid, type_


def get_tree(oid: str, base_path: str = ""):
    result = {}
    for name, oid, type_ in _iter_tree_entries(oid):
        assert "/" not in name
        assert name not in (".", "..")

        path = base_path + "/" + name

        if type_ == "blob":
            result[path] = oid
        elif type_ == "tree":
            result.update(get_tree(oid, path))
        else:
            raise Exception(f"Unknown tree entry of type {type_}")

    return result


def _empty_dir():
    for root, dirnames, filenames in os.walk(data.find_repo("."), topdown=False):
        for filename in filenames:
            path = os.path.realpath(f"{root}/{filename}")
            if is_ignore(path) or not os.path.isfile(path):
                continue
            os.remove(path)

        for dirname in dirnames:
            path = os.path.realpath(f"{root}/{dirname}")
            if is_ignore(path) or not os.path.isdir(path):
                continue
            try:
                os.rmdir(path)
            except (FileNotFoundError, OSError):
                pass


def read_tree(tree_oid: str):
    _empty_dir()
    tree = get_tree(tree_oid, data.find_repo("."))
    for path, oid in tree.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(data.get_object(oid))


def commit(msg: str) -> str:
    path = data.find_repo(".")
    oid = write_tree(path)
    temp = f"tree {oid}\n"
    head = data.get_HEAD()
    if head:
        temp = f"{temp}parent {head}\n"

    temp = f"{temp}\n{msg}"
    oid = data.hash_obj(temp.encode(), type_="commit")
    data.set_HEAD(oid)
    return oid


def get_commit(oid: str):
    parent, tree = None, None
    commit = data.get_object(oid, "commit")

    lines = commit.splitlines()

    for i in range(len(lines) - 1):
        if lines[i]:
            key, value = lines[i].split(" ", 1)
            if key == "tree":
                tree = value
            elif key == "parent":
                parent = value
            else:
                raise Exception(f"Unknown field {key}")

    msg = lines[-1]
    return Commit(parent=parent, tree=tree, message=msg)

def checkout(oid: str):
    commit = get_commit(oid)
    read_tree(commit.tree)
    data.set_HEAD(oid)

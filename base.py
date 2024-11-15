import os
import data


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

    tree = "".join(f"{name} {oid} {type_}" for name, oid, type_ in sorted(entires))

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


def read_tree(tree_oid: str):
    tree = get_tree(tree_oid, data.find_repo("."))
    for path, oid in tree.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(data.get_object(oid))

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


def is_ignore(path: str):
    return ".byog" in path.split("/")

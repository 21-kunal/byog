import os
import data


def write_tree(dir: str):
    entires = []
    with os.scandir(dir) as files:
        for file in files:
            if file.is_file(follow_symlinks=False):
                # TODO: write the file to object store
                type_ = "blob"
                oid = data.hash_obj(os.path.realpath(file.path))
            elif file.is_dir(follow_symlinks=False):
                type_ = "tree"
                oid = write_tree(os.path.realpath(file))

            entires.append((file.name, oid, type_))


def is_ignore(path: str):
    return ".byog" in path.split("/")

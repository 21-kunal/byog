import os
import data


def write_tree(dir: str):
    with os.scandir(dir) as files:
        for file in files:
            if file.is_file(follow_symlinks=False):
                # TODO: write the file to object store
                print(os.path.realpath(file))
            elif file.is_dir(follow_symlinks=False):
                write_tree(os.path.realpath(file))

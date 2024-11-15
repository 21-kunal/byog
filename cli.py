import argparse
import data
import os
import base


def main():
    args = parse_args()
    args.func(args)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="byog", description="The stupidest content tracker"
    )

    commands = parser.add_subparsers(title="Command", dest="command")
    commands.required = True

    init_parser = commands.add_parser(
        "init", description="Initialize a new, empty repository."
    )
    init_parser.add_argument(
        "path", default=".", nargs=1, help="Where to create a repository."
    )
    init_parser.set_defaults(func=init)

    hash_obj_parser = commands.add_parser(
        "hash-object",
        description="For storing given file in .byog/objects",
    )
    hash_obj_parser.add_argument(
        "path", nargs=1, type=str, help="Path to a file which has to hash."
    )
    hash_obj_parser.set_defaults(func=hash_obj)

    cat_file_parser = commands.add_parser(
        "cat-file", description="Outputs the object related ot OID."
    )
    cat_file_parser.add_argument(
        "oid",
        nargs=1,
        type=str,
        help="Object ID which you get when using 'hash-object'.",
    )
    cat_file_parser.set_defaults(func=cat_file)

    write_tree_parser = commands.add_parser(
        "write-tree", description="For storing whole directory in .byog/objects"
    )
    write_tree_parser.set_defaults(func=write_tree)

    return parser.parse_args()


def init(args):
    data.init(path=args.path[0])


def hash_obj(args):
    path = args.path[0]
    if os.path.isfile(os.path.realpath(path)):
        with open(path, "rb") as f:
            oid = data.hash_obj(f.read())
            return oid
    else:
        raise Exception(f'Given file path "{path}" is not correct.')


def cat_file(args):
    file_data = data.get_object(args.oid[0])
    print(file_data)


def write_tree(args):
    repo_path = data.find_repo(".")
    base.write_tree(dir=repo_path)

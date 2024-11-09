import argparse
from os import path
from . import data


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
        description="Hash the give file. And stores in .byog/objects",
    )
    hash_obj_parser.add_argument(
        "path", nargs=1, type=str, help="Path to a file which has to hash."
    )
    hash_obj_parser.set_defaults(func=hash_obj)

    return parser.parse_args()


def init(args):
    data.init(path=args.path[0])


def hash_obj(args):
    data.hash_obj(path=args.path[0])

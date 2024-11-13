import argparse
import data


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

    return parser.parse_args()


def init(args):
    data.init(path=args.path[0])


def hash_obj(args):
    oid = data.hash_obj(path=args.path[0])
    print(f"The Object ID(OID) is {oid}")


def cat_file(args):
    file_data = data.cat_file(args.oid[0])
    print(file_data)

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

    oid = base.get_oid

    init_parser = commands.add_parser(
        "init", description="Initialize a new, empty repository."
    )
    init_parser.add_argument("path", default=".", help="Where to create a repository.")
    init_parser.set_defaults(func=init)

    hash_obj_parser = commands.add_parser(
        "hash-object",
        description="For storing given file in .byog/objects",
    )
    hash_obj_parser.add_argument(
        "path", type=str, help="Path to a file which has to hash."
    )
    hash_obj_parser.set_defaults(func=hash_obj)

    cat_file_parser = commands.add_parser(
        "cat-file", description="Outputs the object related ot OID."
    )
    cat_file_parser.add_argument(
        "oid",
        type=oid,
        help="Object ID which you get when using 'hash-object'.",
    )
    cat_file_parser.set_defaults(func=cat_file)

    write_tree_parser = commands.add_parser(
        "write-tree", description="For storing working tree in .byog/objects"
    )
    write_tree_parser.set_defaults(func=write_tree)

    read_tree_parser = commands.add_parser(
        "read-tree", description="Read the work tree realted to OID."
    )
    read_tree_parser.add_argument(
        "tree", type=oid, help="Object ID which you get when using write-tree."
    )
    read_tree_parser.set_defaults(func=read_tree)

    commit_parser = commands.add_parser(
        "commit", description="Records the staged changes in the repository."
    )
    commit_parser.add_argument(
        "-m", "--message", type=str, help="Message for the commit.", required=True
    )
    commit_parser.set_defaults(func=commit)

    log_parser = commands.add_parser("log", description="Logs all the commits.")
    log_parser.add_argument(
        "oid", nargs="?", type=oid, default="@", help="Logs will start from this oid."
    )
    log_parser.add_argument("--oneline", action="store_true", help="One line logs.")
    log_parser.set_defaults(func=log)

    checkout_parser = commands.add_parser(
        "checkout", description="Allows to move to a commit."
    )
    # checkout_parser.add_argument("oid", type=oid, help="Hash of the commit.")
    checkout_parser.add_argument("commit", help="Hash of the commit.")
    checkout_parser.set_defaults(func=checkout)

    tag_parser = commands.add_parser("tag", description="Add tag/names to commit hash.")
    tag_parser.add_argument("name", type=str, help="Name of the tag")
    tag_parser.add_argument("oid", type=oid, default="@", nargs="?", help="Hash of the commit.")
    tag_parser.set_defaults(func=tag)

    k_parser = commands.add_parser("k", description="visualize all the refs and the commits.")
    k_parser.set_defaults(func=k)

    branch_parser = commands.add_parser("branch", description="Create branch.")
    branch_parser.add_argument("name", nargs="?", type=str, help="Name of the branch.")
    branch_parser.add_argument(
        "start_point", 
        default='@', 
        type=oid, 
        nargs="?", 
        help="Ref or hash of a commit. By default HEAD."
    )
    branch_parser.set_defaults(func=branch)
 
    statue_parser = commands.add_parser(
        "status", 
        description="Useful information about the working repo."
    )
    statue_parser.set_defaults(func=status)

    return parser.parse_args()


def init(args: argparse.Namespace):
    base.init(path=args.path)


def hash_obj(args: argparse.Namespace):
    path = args.path
    if os.path.isfile(os.path.realpath(path)):
        with open(path, "rb") as f:
            oid = data.hash_obj(f.read())
            print(oid)
    else:
        raise Exception(f'Given file path "{path}" is not correct.')


def cat_file(args: argparse.Namespace):
    file_data = data.get_object(args.oid)
    print(file_data)


def write_tree(args: argparse.Namespace):
    repo_path = data.find_repo(".")
    oid = base.write_tree(dir=repo_path)
    print(oid)


def read_tree(args: argparse.Namespace):
    base.read_tree(args.tree)


def commit(args: argparse.Namespace):
    oid = base.commit(args.message)
    print(oid)


def log(args: argparse.Namespace):

    for oid in base.iter_commits_and_parents({args.oid}):
        commit: base.Commit = base.get_commit(oid)

        if args.oneline:
            print(f"\033[33m{oid[:7]}\033[0m  {commit.message}")
        else:
            print(f"\033[33mcommit {oid}\033[0m")
            print(f"  {commit.message}")
            print("")


def checkout(args: argparse.Namespace):
    base.checkout(args.commit)


def tag(args: argparse.Namespace):
    base.create_tag(args.name, args.oid)

def k(args: argparse.Namespace):
    dot = "digraph commits {\n"
    oids = set()
    for refname, ref in data.iter_refs(deref=False):
        dot += f'"{refname}" [shape=note]\n'
        dot += f'"{refname}" -> "{ref.value}"\n'

        if not ref.symbolic:
            oids.add(ref.value)

    for oid in base.iter_commits_and_parents(oids):
        commit = base.get_commit(oid)
        dot += f'"{oid}" [shape=box style=filled label="{oid[:10]}"]\n'

        if commit.parent :
            dot += f'"{oid}" -> "{commit.parent}"\n'

    dot += "}"
    print("\033[33mUse Graphviz (with dot) to visualize the refs and commit graph.\033[0m\n")
    print(dot)
    
def branch(args: argparse.Namespace):
    if not args.name:
        current = base.get_branch_name()
        for branch in base.iter_branch_names():
            prefix = "*" if branch == current else " "
            print(f"\033[32m {prefix}{branch}\033[0m")
    else:
        base.create_branch(args.name, args.start_point)
        print(f"Branch {args.name} created at {args.start_point[:10]}")


def status(args: argparse.Namespace):
    HEAD = base.get_oid("@")
    branch = base.get_branch_name()

    if branch:
        print(f"\033[33mOn branch {branch}\033[0m\n")
    else:
        print(f"HEAD detached at {HEAD[:10]}")



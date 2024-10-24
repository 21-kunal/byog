import argparse
import collections
import configparser
import grp
import hashlib
import os
import pwd
import re
import zlib
from datetime import datetime
from fnmatch import fnmatch
from math import ceil

argParser = argparse.ArgumentParser(description="The stupidest content tracker.")
argSubParsers = argParser.add_subparsers(title="Commands", dest="command")
argSubParsers.required = True


class GitRepository(object):
    "A git repository"

    workTree = None
    gitDir = None
    conf = None

    def __init__(self, path, force=False):
        self.workTree = path
        self.gitDir = os.path.join(path, ".git")

        if not (force or os.path.isdir(self.gitDir)):
            raise Exception(f"Not a Git repository {path}")

        # Read configuration file in .git/config
        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration file missing")

        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception(f"Unsupported repositoryformatversion {vers}")


def repo_path(repo: GitRepository, *path) -> str:
    """Compute path under repo's gitDir."""
    return os.path.join(repo.gitDir, *path)


def repo_dir(repo: GitRepository, *path, mkdir: bool = False) -> str | None:
    """Similar to repo_path, but creates the specified directory if it doesn't
    exist and mkdir is True."""

    path = repo_path(repo, *path)

    if os.path.exists(path):

        if os.path.isdir(path):
            return path
        else:
            raise Exception(f"Not a directory {path}")

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None


def repo_file(repo: GitRepository, *path, mkdir: bool = False) -> str | None:
    """Same as repo_path, but create dirname(*path) if absent.  For
    example, repo_file(r, \"refs\", \"remotes\", \"origin\", \"HEAD\") will create
    .git/refs/remotes/origin."""

    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)

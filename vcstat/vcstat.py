#!/usr/bin/env python3

import os
import sys
import argparse
from git import Repo  # from 'GitPython' pkg


RED = "\033[0;31m"
GREEN = "\033[0;32m"
DEFAULT = "[0m"
DIRTY = f"{RED}dirty\033{DEFAULT}"
CLEAN = f"{GREEN}clean\033{DEFAULT}"

STATUS_TEMPLATE = "\033[1;37m{basename}\033[0m ({dirty}) \033[0;33m{branch}\033[0m"
DEFAULT_PADDING = 2
GIT_DIR = ".git"


# FIXME: change this to format_status() & return a string for printing
# TODO: add bash colours to status output?
# TODO: add flag to ignore untracked files?
def print_git_status(repo,
                     padding_size=0,
                     show_git_status=False,
                     show_dirty_only=False):
    """
    Print Git repository status to `stdout`.

    @param repo: git Repo object
    @param padding_size: number of spaces to indent the repository name
    @param show_git_status: True to list all modified and untracked files
    @param show_dirty_only: True prevents display of unmodified repositories
    """
    show_clean_repo = not show_dirty_only  # reverse flag for readability
    basename = os.path.basename(repo.working_dir)

    formatting = {"basename": basename,
                  "dirty": DIRTY if repo.is_dirty() else CLEAN,
                  'branch': repo.head.ref.name}

    text = STATUS_TEMPLATE.format(**formatting)

    if show_git_status:
        # show more extended form output for 'git status'
        status_text = repo.git.status("--short")

        if status_text:
            # show dirty repos with modified & untracked files in status_text
            out = "\n".join(f"{padding_size * ' '}{line}" for line in status_text.split('\n'))
            print(f"{text}\n{out}\n")
        else:
            if show_clean_repo:
                print(f"{text}\n")
    else:
        # ignore git status, show short form summary of repo status
        if show_clean_repo or repo.is_dirty():
            pad = (padding_size - len(basename))
            print(pad * ' ', text)


def _basename_lower(term: Repo):
    return os.path.basename(term.working_dir).lower()


if __name__ == "__main__":
    desc = "Show git status for multiple repositories"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("dirs", default=[os.getcwd()], nargs='*',
                        help="Set root search directories")

    parser.add_argument("-s", "--status",
                        default=False,
                        action="store_true",
                        help="Show git status")

    parser.add_argument("-d", "--dirty-only",
                        default=False,
                        action="store_true",
                        help="Show only dirty/modified repos (inc untracked files)")

    args = parser.parse_args()

    for _dir in args.dirs:
        git_projects = []  # split printout of each dir
        for root, dirs, _ in os.walk(_dir):
            if GIT_DIR in dirs:
                repo = Repo(root)

                if repo.is_dirty() or args.dirty_only is False:
                    git_projects.append(repo)

        if git_projects:
            print(f'Git Repos {_dir}:')
            longest = max([len(os.path.basename(repo.working_dir)) for repo in git_projects])

            for repo in sorted(git_projects, key=_basename_lower):
                padding = DEFAULT_PADDING if args.status else longest
                print_git_status(repo, padding, args.status, args.dirty_only)
        else:
            sys.exit("No repositories found")

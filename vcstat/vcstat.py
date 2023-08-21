#!/usr/bin/env python3

import os
import sys
import argparse
from git import Repo  # from 'GitPython' pkg


RED = "\033[0;31m"
GREEN = "\033[0;32m"
DEFAULT = "[0m"
DIRTY = f'{RED}dirty\033{DEFAULT}'
CLEAN = f'{GREEN}clean\033{DEFAULT}'

STATUS_TEMPLATE = '\033[1;37m{path}\033[0m ({dirty}) \033[0;33m{branch}\033[0m'


# FIXME: change this to format_status() & return a string for printing
# TODO: add bash colours to status output?
def print_git_status(repo_path,
                     padding_size=0,
                     show_git_status=False,
                     show_dirty_only=False):
    """TODO"""
    show_clean_repo = not show_dirty_only  # reverse flag for readability
    base_name = os.path.basename(repo_path)
    repo = Repo(repo_path)

    stats = {'path': base_name,
             'dirty': DIRTY if repo.is_dirty() else CLEAN,
             'branch': repo.head.ref.name}

    tmp = STATUS_TEMPLATE.format(**stats)

    if show_git_status:
        # show long form output for git status
        status_text = repo.git.status("--short")

        if status_text:
            # show dirty repos with modified & untracked files in status_text
            out = "\n".join(f"{padding_size * ' '}{line}" for line in status_text.split('\n'))
            print(f"{tmp}\n{out}\n")
        else:
            if show_clean_repo:
                print(f"{tmp}\n")

    else:
        # ignore git status, show short form summary of repo status
        if show_clean_repo or repo.is_dirty():
            pad = (padding_size - len(base_name))
            print(pad * ' ', tmp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show git status for multiple repositories")
    parser.add_argument("dirs", default=[os.getcwd()], nargs='+',
                        help="Set root search directories")

    parser.add_argument("-s", "--status", default=False, action="store_true",
                        help="Show git status")

    parser.add_argument("-d", "--dirty-only", default=False, action="store_true",
                        help="Show only dirty/modified repos (inc untracked files)")

    args = parser.parse_args()
    git_projects = []

    for _dir in args.dirs:
        for root, dirs, _ in os.walk(_dir):
            if ".git" in dirs:
                git_projects.append(root)

    if git_projects:
        print('Git:')
        longest = max([len(os.path.basename(e)) for e in git_projects])

        for p in sorted(git_projects):
            print_git_status(p, 2 if args.status else longest, args.status, args.dirty_only)
    else:
        sys.exit("No repositories found")

#!/usr/bin/env python3

import os
import sys
import argparse
import git  # GitPython package


RED = "\033[0;31m"
GREEN = "\033[0;32m"
DEFAULT = "[0m"
DIRTY = f"{RED}dirty\033{DEFAULT}"
CLEAN = f"{GREEN}clean\033{DEFAULT}"

DEFAULT_PADDING = 2
GIT_DIR = ".git"


# TODO: add bash colours to status output?
def get_git_status(repo: git.Repo,
                   padding_size=0,
                   show_git_status=False,
                   show_untracked=False):
    """
    Returns Git repository status report.

    @param repo: git Repo object
    @param padding_size: number of spaces to indent the repository name
    @param show_git_status: True to list all modified and untracked files
    @param show_untracked: True displays flag if untracked files in repository
    """
    basename = os.path.basename(repo.working_dir)
    n_untracked = len(repo.untracked_files)
    comment = f" [+{n_untracked} untracked]" if show_untracked and repo.untracked_files else ""
    dirty = DIRTY if repo.is_dirty() else CLEAN
    branch = repo.head.ref.name
    text = f"\033[1;37m{basename}\033[0m ({dirty}) \033[0;33m{branch}\033[0m{comment}"

    if show_git_status:
        # an extended form output for 'git status' option
        status = repo.git.status("--short")
        lines = ""

        if status:
            # show dirty repos & list modified & untracked files
            lines = "\n".join(f"{padding_size * ' '}{line}" for line in status.split("\n"))
        return f"{text}\n{lines}\n"

    # default: show 1 liner summary of repo status
    pad = padding_size - len(basename)
    return f"{pad * ' '} {text}"


def _basename_lower(repo: git.Repo):
    return os.path.basename(repo.working_dir).lower()


if __name__ == "__main__":
    desc = """Show git status for multiple repositories. Given one or more dirs,
           vcstat searches for git repositories, listing the git status of each."""
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("dirs", default=[os.getcwd()], nargs='*',
                        help="Set root search directories")

    parser.add_argument("-a", "--all",
                        default=False,
                        action="store_true",
                        help="Show status of all clean & dirty repositories")

    parser.add_argument("-s", "--status",
                        default=False,
                        action="store_true",
                        help="Show longer form git status for each repository")

    parser.add_argument("-u", "--untracked",
                        default=False,
                        action="store_true",
                        help="""Alert repositories with untracked files. Clean
                            repositories with untracked files are treated as
                            modified & included in the short form output.""")

    args = parser.parse_args()

    for i, _dir in enumerate(args.dirs):
        git_repos = []  # split printout of each dir
        for root, dirs, _ in os.walk(_dir):
            if GIT_DIR in dirs:
                repo = git.Repo(root)

                # filter repos for inclusion
                if repo.is_dirty() or args.all or (args.untracked and repo.untracked_files):
                    git_repos.append(repo)

        if git_repos:
            spacer = "\n" if i else ""  # add newlines between repo groups per arg
            print(f"{spacer}Git Repos {_dir}:")
            longest = max([len(os.path.basename(repo.working_dir)) for repo in git_repos])

            for repo in sorted(git_repos, key=_basename_lower):
                padding = DEFAULT_PADDING if args.status else longest
                print(get_git_status(repo, padding, args.status, args.untracked))
        else:
            sys.exit("No repositories found")

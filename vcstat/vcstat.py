#!/usr/bin/env python3

import os
import sys
from git import Repo  # from 'GitPython' pkg


RED = "\033[0;31m"
GREEN = "\033[0;32m"
DEFAULT = "[0m"
DIRTY = f'{RED}dirty\033{DEFAULT}'
CLEAN = f'{GREEN}clean\033{DEFAULT}'

STATUS_TEMPLATE = '\033[1;37m{path}\033[0m ({dirty}) \033[0;33m{branch}\033[0m'


def print_git_status(repo_path, padding_size=0):
    base_name = os.path.basename(repo_path)
    repo = Repo(repo_path)

    stats = {'path': base_name,
             'dirty': DIRTY if repo.is_dirty() else CLEAN,
             'branch': repo.head.ref.name}

    tmp = STATUS_TEMPLATE.format(**stats)
    print((padding_size - len(base_name)) * ' ', tmp)


git_projects = []
search_dirs = sys.argv[1:] or ['.']

for _dir in search_dirs:
    for root, dirs, _ in os.walk(_dir):
        for d in dirs:
            if d == '.git':
                git_projects.append(root)

if git_projects:
    print('Git:')
    longest = max([len(os.path.basename(e)) for e in git_projects])
    for p in sorted(git_projects):
        print_git_status(p, longest)
    print()

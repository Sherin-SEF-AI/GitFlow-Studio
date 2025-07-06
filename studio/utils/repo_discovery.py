import os

def discover_git_repos(start_path, max_depth=4):
    repos = []
    for root, dirs, files in os.walk(start_path):
        if '.git' in dirs:
            repos.append(root)
            # Do not recurse into subdirs of a repo
            dirs[:] = []
        # Limit recursion depth
        if os.path.relpath(root, start_path).count(os.sep) >= max_depth:
            dirs[:] = []
    return repos 
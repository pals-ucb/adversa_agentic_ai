import os

def find_workspace_root(start_path: str = __file__) -> str:
    """
    Traverses upward from the given path until it finds a marker of the workspace root,
    such as a .git directory or pyproject.toml file.
    """
    path = os.path.abspath(os.path.dirname(start_path))
    while path != os.path.dirname(path):  # until we reach the filesystem root
        if os.path.exists(os.path.join(path, ".git")) or os.path.exists(os.path.join(path, "pyproject.toml")):
            return path
        path = os.path.dirname(path)
    return os.path.abspath(os.path.dirname(start_path))  # fallback

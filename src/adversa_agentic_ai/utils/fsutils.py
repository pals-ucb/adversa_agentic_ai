import os

def find_workspace_root(marker_dir: str = "adversa_agentic_ai") -> str:
    """
    Walks up from the current file’s directory until it finds
    a directory named `marker_dir`, and returns its path.
    Raises RuntimeError if not found.
    """
    path = os.path.abspath(os.path.dirname(__file__))
    while True:
        if os.path.basename(path) == marker_dir:
            return path
        parent = os.path.dirname(path)
        if parent == path:
            # we’ve reached the filesystem root
            break
        path = parent
    raise RuntimeError(f"Could not find workspace root '{marker_dir}' in any parent of {__file__}")

import os

_util_dir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(_util_dir, ".."))


def join_path(base: str, *args) -> str:
    """
    Join the base path with a series of directories. (Wrapper on `os.path.join`)

    Args:
        base: String to use as the base of the path.
        args: Any number of additional elements to be added to the path.

    Returns:
        os-appropriate path. (note: path may or may not actually exist)
    """
    return os.path.join(base, *args)

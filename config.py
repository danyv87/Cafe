import os


def get_data_path(filename: str) -> str:
    """Return absolute path for a data file.

    The base directory is taken from the ``CAFE_DATA_PATH`` environment
    variable. If not set, it defaults to a ``data`` subdirectory in the
    current working directory.
    """
    base_dir = os.environ.get("CAFE_DATA_PATH", os.path.join(os.getcwd(), "data"))
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, filename)

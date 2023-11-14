from pathlib import Path


def check_file_path(file_path: str):
    """
    This method checks if the filepath is valid. Raises a FileNotFoundError if it's invalid.
    :param file_path: The path to the csv file.
    """
    valid = Path(file_path).exists()
    if not valid:
        raise FileNotFoundError(f"Filepath: {file_path} is not valid.")
    return True








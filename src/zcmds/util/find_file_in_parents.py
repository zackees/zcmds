import os


def find_file_in_parents(
    start_dir: str, filename: str, max_levels: int = 3
) -> tuple[str, int]:
    """
    Find a file by looking in the current directory and up to max_levels parent directories.

    Args:
        start_dir: The directory to start searching from
        filename: The name of the file to search for
        max_levels: The maximum number of parent directories to search automatically

    Returns:
        A tuple containing the path to the file and the number of levels up it was found.
        If the file is not found, returns ("", -1).
    """
    MAX_ITERATIONS = 20  # Safety limit to prevent infinite loops

    current_dir = start_dir
    for level in range(max_levels + 1):  # +1 to include current directory (level 0)
        file_path = os.path.join(current_dir, filename)
        if os.path.exists(file_path):
            return file_path, level

        # Move up one directory
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # We've reached the root directory
            break
        current_dir = parent_dir

    # Continue searching beyond max_levels
    level = max_levels + 1
    iterations = 0

    while iterations < MAX_ITERATIONS:
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # We've reached the root directory
            break

        current_dir = parent_dir
        level += 1
        iterations += 1

        file_path = os.path.join(current_dir, filename)
        if os.path.exists(file_path):
            return file_path, level

    if iterations >= MAX_ITERATIONS:
        print(
            f"Warning: Exceeded maximum path iterations ({MAX_ITERATIONS}) while searching for {filename}"
        )

    return "", -1  # Not found

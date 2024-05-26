"""General functions to simplify code"""

def get_numbers(string):
    """Extracts all numbers from a string and returns them as a list."""
    return [i for i in ''.join((ch if ch.isdigit() else ' ') for ch in string).split()]

def replace_second_part_in_path(path, name):
    """Replaces the second part of a path with a new name."""
    parts = path.split("/")
    if len(parts) > 1:
        parts[1] = name
    return "/".join(parts)

def get_folder_name_from_path(path):
    """Extracts the folder name from a path."""
    return path.split("/")[0] if "/" in path else ""
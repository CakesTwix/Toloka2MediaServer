"""General functions to simplify code"""

def get_numbers(string):
    """Returns a list of numbers from the string"""
    raw = "".join((ch if ch in "0123456789" else " ") for ch in string)
    return list(i for i in raw.split())

def replace_second_part_in_path(path, name):
    parts = path.split("/")
    if len(parts) > 1:
        parts[1] = name
    return "/".join(parts)

def get_folder_name_from_path(path):
    parts = path.split("/")
    if len(parts) > 1:
        return parts[0]
    return ""
"""General functions to simplify code"""

import re


def get_numbers(string):
    """Extracts all numbers from a string and returns them as a list."""
    return [i for i in "".join((ch if ch.isdigit() else " ") for ch in string).split()]


def replace_second_part_in_path(path, name):
    """Replaces the second part of a path with a new name."""
    parts = path.split("/")
    if len(parts) > 1:
        parts[1] = name
    return "/".join(parts)


def get_folder_name_from_path(path):
    """Extracts the folder name from a path."""
    return path.split("/")[0] if "/" in path else ""


def extract_torrent_details(torrent_name):
    matched_name = re.search(r"[\/|]([^\/|\(]+)", torrent_name)
    matched_year = re.search(r"\((\d{4})\)", torrent_name)

    if matched_name:
        suggested_name = f"{matched_name.group(1) if matched_name else ''} ({matched_year.group(1) if matched_year else ''})".strip()
        suggested_name = re.sub(r"\s+", " ", suggested_name)
        suggested_codename = re.sub(r"\W+", "", matched_name.group(1)).strip()
    else:
        suggested_name = "No match found"
        suggested_codename = "No match found"

    return suggested_name, suggested_codename

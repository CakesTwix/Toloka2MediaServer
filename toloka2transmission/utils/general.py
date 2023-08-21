"""General functions to simplify code"""


def get_numbers(string):
    """Returns a list of numbers from the string"""
    raw = "".join((ch if ch in "0123456789" else " ") for ch in string)
    return list(i for i in raw.split())

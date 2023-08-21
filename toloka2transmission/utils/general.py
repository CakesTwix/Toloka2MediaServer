"""General functions to simplify code"""


def getNumbers(string):
    """Returns a list of numbers from the string"""
    raw = "".join((ch if ch in "0123456789" else " ") for ch in string)
    return [i for i in raw.split()]

import argparse

def get_parser():
    # Setup argparse
    parser = argparse.ArgumentParser(description="Console utility for updating torrents from Toloka.")

    # Create argument groups
    main_group = parser.add_argument_group('Main Arguments')
    add_group = parser.add_argument_group('Add Release Arguments')
    util_group = parser.add_argument_group('Utility Arguments')

    # Main Arguments
    main_group.add_argument("-c", "--codename", type=str, help="Codename of the title", required=False)
    main_group.add_argument("-a", "--add", nargs='?', const="default", help="Add new release to config", required=False)

    # Utility Arguments
    util_group.add_argument("-n", "--num", type=str, help="Get list of numbers from string", required=False)
    util_group.add_argument("-f", "--force", action='store_true', help="Force download regardless of torrent presence", required=False)

    # Add Release Arguments
    add_group.add_argument("-u", "--url", type=str, help="Toloka URL to release", required=False)
    add_group.add_argument("-s", "--season", type=str, help="Season number", required=False)
    add_group.add_argument("-i", "--index", type=int, help="Series index", required=False)
    add_group.add_argument("-co", "--correction", type=int, help="Adjusted series number", required=False)
    add_group.add_argument("-t", "--title", type=str, help="Series name", required=False)
    
    return parser
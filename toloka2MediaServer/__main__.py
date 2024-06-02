"""Entering the program, this is where it all starts"""
import sys
from toloka2MediaServer.args_parser import get_parser
from toloka2MediaServer.clients.dynamic import dynamic_client_init
from toloka2MediaServer.config_parser import get_toloka_client, load_configurations
from toloka2MediaServer.logger_setup import setup_logging

from toloka2MediaServer.main_logic import add_release_by_name, add_release_by_url, update_release_by_name, update_releases
from toloka2MediaServer.models.application import config_to_app
from toloka2MediaServer.utils.general import get_numbers

def main():
    app_config, titles_config = load_configurations()
    application_config = config_to_app(app_config)
    parser = get_parser()
    args = parser.parse_args()
    logger = setup_logging(app_config["Python"]["logging"])
    logger.info("------------------------------------------")
    
    client = dynamic_client_init(application_config)
    toloka = get_toloka_client(application_config)
    
    # Output numbers if requested
    if args.num:
        print(get_numbers(args.num))
        sys.exit()

    if args.url:
        #--add --url https://toloka.to/t675888 --season 02 --index 2 --correction 0 --title "Tsukimichi -Moonlit Fantasy-"
        logger.debug(f"--add {args.add} --url {args.url} --season {args.season} --index{args.index} --correction{args.correction} --title{args.title}")
        add_release_by_url(args, logger, toloka, client, application_config, titles_config)
        sys.exit()

    # Adding new title
    if args.add:
        #--add "Tsuki ga Michibiku Isekai Douchuu (Season 2)"
        logger.debug(f"--add {args.add}")
        add_release_by_name(args, logger, toloka, client, application_config, titles_config)
        sys.exit()

    # Update specific or all anime
    if args.codename:
        logger.debug(f"--codename {args.codename}")
        update_release_by_name(args, args.codename, logger, toloka, client, application_config, titles_config)
    else:
        logger.debug(f"no args, update all")
        update_releases(args, logger, toloka, client, application_config, titles_config)

    sys.exit()
    
if __name__ == '__main__':
    main()
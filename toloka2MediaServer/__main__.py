"""Entering the program, this is where it all starts"""

import sys
from toloka2MediaServer.args_parser import get_parser
from toloka2MediaServer.clients.dynamic import dynamic_client_init
from toloka2MediaServer.config_parser import get_toloka_client, load_configurations
from toloka2MediaServer.logger_setup import setup_logging

from toloka2MediaServer.main_logic import (
    add_release_by_name,
    add_release_by_url,
    update_release_by_name,
    update_releases,
)
from toloka2MediaServer.models.config import Config
from toloka2MediaServer.utils.general import get_numbers


def main():
    # cli entry point to perform direct operation using terminal\console
    # app_config - generic configuration of application - based on app.ini
    # mainly used in clients to get bittorent connection details or for logging
    # titles_config - titles configuration of application - based on titles.ini
    # widely used all over application, as main db to store and process titles
    # application_config - Toloka section of app.ini converted to Application class for easy use.

    app_config, titles_config, application_config = load_configurations()
    parser = get_parser()
    args = parser.parse_args()
    logger = setup_logging(app_config["Python"]["logging"])
    logger.info("------------------------------------------")

    config = Config(
        args=args,
        logger=logger,
        toloka=get_toloka_client(application_config),
        app_config=app_config,
        titles_config=titles_config,
        application_config=application_config,
    )

    config.client = dynamic_client_init(config)

    # Output numbers if requested
    if args.num:
        print(get_numbers(args.num))
        sys.exit()

    # Add new title using existing url and bypass user input by default\generated values. Require minimum of url, season, index, correction and title
    # to add new title. works simmilar to add, but without user interaction
    if args.url:
        # --add --url https://toloka.to/t675888 --season 02 --index 2 --correction 0 --title "Tsukimichi -Moonlit Fantasy-"
        logger.debug(
            f"--add {args.add} --url {args.url} --season {args.season} --index{args.index} --correction{args.correction} --title{args.title} --path{args.path}"
        )
        response = add_release_by_url(config)
        logger.debug(response)
        sys.exit()

    # Adding new title. Expect user input to finish operation
    if args.add:
        # --add "Tsuki ga Michibiku Isekai Douchuu (Season 2)"
        logger.debug(f"--add {args.add}")
        response = add_release_by_name(config)
        logger.debug(response)
        sys.exit()

    # Update specific or all anime
    # Update done by compare of published date on release page
    if args.codename:
        # Updates existing title from titles.ini based on provided codename. No user input required.
        logger.debug(f"--codename {args.codename}")
        response = update_release_by_name(config)
        logger.debug(response)
    else:
        # Update all listed titles from titles.ini
        logger.debug(f"no args, update all")
        response = update_releases(config)
        logger.debug(response)

    sys.exit()


if __name__ == "__main__":
    main()

from setuptools import setup, find_packages

setup(
    name="toloka2MediaServer",
    version="0.2.1",
    description="Addon to facilitate locating and adding TV series/anime torrents from Toloka/Hurtom with standardized naming for Sonarr/Plex/Jellyfin integration.",
    url="https://github.com/CakesTwix/toloka2MediaServer",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'toloka2MediaServer': ['data/*'],
    },
    entry_points={
        'console_scripts': [
            'toloka2MediaServer=toloka2MediaServer.main:main',
        ],
    },
    install_requires=[
        'transmission_rpc',
        'qbittorrent-api',
        'requests',
        'toloka2python @ git+https://github.com/maksii/toloka2python'
    ]
)
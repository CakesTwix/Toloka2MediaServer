"""Here we work with config files and some toloka"""
import configparser
from toloka2python import Toloka

app, titles = configparser.ConfigParser(), configparser.ConfigParser()
app.read("app.ini")
titles.read("titles.ini")

toloka = Toloka(app["Toloka"]["username"], app["Toloka"]["password"])

"""Here we work with config files and some toloka"""
import configparser
from toloka2python import Toloka

app, titles = configparser.ConfigParser(), configparser.ConfigParser()
app.read("toloka2anime/data/app.ini")
titles.read("toloka2anime/data/titles.ini")

toloka = Toloka(app["Toloka"]["username"], app["Toloka"]["password"])
selectedClient = app["Toloka"]["client"]
"""Here we work with config files"""
import configparser

app, titles = configparser.ConfigParser(), configparser.ConfigParser()
app.read("app.ini")
titles.read("titles.ini")

import logging
from flask import Flask, request, render_template
import sys

import toloka2MediaServer.main_logic
sys.path.insert(1, '../toloka2MediaServer')
import toloka2MediaServer

app = Flask(__name__)
logger = logging.basicConfig(
    filename='toloka2MediaServer/data/app_web.log',  # Name of the file where logs will be written
    filemode='a',  # Append mode, which will append the logs to the file if it exists
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of the log messages
    level=logging.DEBUG #log level from config
)
class RequestData:
    url: str = ""
    season: int = 0
    index: int = 0
    correction: int = 0
    title: str = ""
    def __init__(self, url = "", season = 0, index = 0, correction = 0, title = ""):
        self.url = url
        self.season = season
        self.index = index
        self.correction = correction
        self.title = title


@app.route('/', methods=['GET', 'POST'])


def index():
    titles = toloka2MediaServer.main_logic.titles
    # Creating a list of dictionaries, each containing the data for the selected keys
    data = []
    keys = ['torrent_name', 'publish_date', 'guid']
    for section in titles.sections():
        section_data = {'codename': section}
        for key in keys:
            section_data[key] = titles.get(section, key)
        data.append(section_data)

    # Define column headers and rename them
    columns = {
        'codename': 'Codename',
        'torrent_name': 'Name',
        'publish_date': 'Last Updated',
        'guid': 'URL'
    }
        
    if request.method == 'POST':
        requestData = RequestData(
            url = request.form['url'],
            season = request.form['season'],
            index = int(request.form['index']),
            correction = int(request.form['correction']),
            title = request.form['title'],
        )
        
        
        #--add --url https://toloka.to/t675888 --season 02 --index 2 --correction 0 --title "Tsukimichi -Moonlit Fantasy-"
        
        output = toloka2MediaServer.main_logic.add_release_by_url(requestData, logger)
        return render_template('result.html', output=output)
    return render_template('index.html', data=data, columns=columns)
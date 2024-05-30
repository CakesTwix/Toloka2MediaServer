import logging
from flask import Flask, request, render_template, redirect, url_for, session
import sys

import toloka2MediaServer.config
import toloka2MediaServer.main_logic
sys.path.insert(1, '../toloka2MediaServer')
import toloka2MediaServer

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set this to a strong secret value

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
    codename: str = ""
    force: bool = False
    def __init__(self, url = "", season = 0, index = 0, correction = 0, title = "", codename = "", force=False):
        self.url = url
        self.season = season
        self.index = index
        self.correction = correction
        self.title = title
        self.codename = codename
        self.force = force


@app.route('/', methods=['GET'])
def index():
    titles = toloka2MediaServer.config.update_titles()
    # Creating a list of dictionaries, each containing the data for the selected keys
    data = []
    codenames =[]
    keys = ['torrent_name', 'publish_date', 'guid']
    for section in titles.sections():
        codenames.append(section)
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
    output = session.pop('output', None)   
    return render_template('index.html', data=data, columns=columns, codenames=codenames, output=output)

@app.route('/add_release', methods=['POST'])
def add_release():
    # Process the URL to add release
    try:
        requestData = RequestData(
            url = request.form['url'],
            season = request.form['season'],
            index = int(request.form['index']),
            correction = int(request.form['correction']),
            title = request.form['title'],
        )


        #--add --url https://toloka.to/t675888 --season 02 --index 2 --correction 0 --title "Tsukimichi -Moonlit Fantasy-"

        output = toloka2MediaServer.main_logic.add_release_by_url(requestData, logger)
        message = f'Release added from URL. {output}'
    except Exception as e:
        message = f'Error: {str(e)}'
    session['output'] = message
    return redirect(url_for('index'))

@app.route('/update_release', methods=['POST'])
def update_release():
    # Process the name to update release
    try:
        requestData = RequestData(
            codename = request.form['codename']
        )
        output = toloka2MediaServer.main_logic.update_release_by_name(requestData, requestData.codename, logger)
        message = f'Release updated by name  {output}'
    except Exception as e:
        message = f'Error: {str(e)}'
    session['output'] = message
    return redirect(url_for('index'))

@app.route('/update_all_releases', methods=['POST'])
def update_all_releases():
    # Process to update all releases
    try:
        requestData = RequestData()
        output = toloka2MediaServer.main_logic.update_releases(requestData, logger)

        message = f'All releases updated  {output}'
    except Exception as e:
        message = f'Error: {str(e)}'
    session['output'] = message
    return redirect(url_for('index'))
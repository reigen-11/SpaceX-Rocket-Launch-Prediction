import requests
import pandas as pd
import datetime
from src.api import SPACEX_URL
import pytz
from src.utils.logger import logging
from src.utils.exception import CustomExceptions
import sys


def fetch_data():
    logging.info("Fetching Data from API")
    try:
        response = requests.get(SPACEX_URL)
        if response.status_code == 200:
            data = pd.json_normalize(response.json())

            utc_now = datetime.datetime.now(pytz.utc)
            america_timezone = pytz.timezone('America/New_York')
            america_time = utc_now.astimezone(america_timezone)

            year = america_time.year
            month = america_time.month
            day = america_time.day

            data = data[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]
            data = data[data['cores'].map(len) == 1]
            data = data[data['payloads'].map(len) == 1]

            data['cores'] = data['cores'].map(lambda x: x[0])
            data['payloads'] = data['payloads'].map(lambda x: x[0])

            data['date'] = pd.to_datetime(data['date_utc']).dt.date

            data = data[data['date'] <= datetime.date(year, month, day)]

            return data
        logging.info('Fetched Data Successfully')

    except Exception as e:
        raise CustomExceptions(e, sys)

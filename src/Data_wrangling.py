import os
from api import raw_data_directory, rockets, launch_pad, payloads, cores, SPACEX_URL
from tqdm import tqdm
import pandas as pd
import requests
import datetime
import sys
import pytz
from logger import logging
from exception import CustomExceptions


BoosterVersion = []
PayloadMass = []
Orbit = []
LaunchSite = []
Outcome = []
Flights = []
GridFins = []
Reused = []
Legs = []
LandingPad = []
Block = []
ReusedCount = []
Serial = []
Longitude = []
Latitude = []


def process_data(input_data):
    try:
        getBoosterVersion(input_data)
        getLaunchSite(input_data)
        getPayloadData(input_data)
        getCoreData(input_data)

        launch_dict = {'FlightNumber': list(input_data['flight_number']),
                       'Date': list(input_data['date']),
                       'BoosterVersion': BoosterVersion,
                       'PayloadMass': PayloadMass,
                       'Orbit': Orbit,
                       'LaunchSite': LaunchSite,
                       'Outcome': Outcome,
                       'Flights': Flights,
                       'GridFins': GridFins,
                       'Reused': Reused,
                       'Legs': Legs,
                       'LandingPad': LandingPad,
                       'Block': Block,
                       'ReusedCount': ReusedCount,
                       'Serial': Serial,
                       'Longitude': Longitude,
                       'Latitude': Latitude}

        return pd.DataFrame.from_dict(launch_dict)

    except Exception as e:
        raise CustomExceptions(e, sys)


def getBoosterVersion(input_data):
    for x in tqdm(input_data['rocket'], desc='Fetching Booster Versions',
                  bar_format='{desc}: {bar} | {n_fmt}/{total_fmt} {percentage:3.0f}%'):
        res = requests.get(rockets + str(x)).json()
        BoosterVersion.append(res['name'])


def getLaunchSite(input_data):
    for x in tqdm(input_data['launchpad'], desc='Fetching Launch Sites',
                  bar_format='{desc}: {bar} | {n_fmt}/{total_fmt} {percentage:3.0f}%'):
        res = requests.get(launch_pad + str(x)).json()
        Longitude.append(res['longitude'])
        Latitude.append(res['latitude'])
        LaunchSite.append(res['name'])


def getPayloadData(input_data):
    for load in tqdm(input_data['payloads'], desc='Fetching Payload Data',
                     bar_format='{desc}: {bar} | {n_fmt}/{total_fmt} {percentage:3.0f}%'):
        res = requests.get(payloads + load).json()
        PayloadMass.append(res['mass_kg'])
        Orbit.append(res['orbit'])


def getCoreData(input_data):
    for core in tqdm(input_data['cores'], desc='Fetching Core Data',
                     bar_format='{desc}: {bar} | {n_fmt}/{total_fmt} {percentage:3.0f}%'):
        if core['core'] is not None:
            res = requests.get(cores + core['core']).json()
            Block.append(res['block'])
            ReusedCount.append(res['reuse_count'])
            Serial.append(res['serial'])
        else:
            Block.append(None)
            ReusedCount.append(None)
            Serial.append(None)
        Outcome.append(str(core['landing_success']) + ' ' + str(core['landing_type']))
        Flights.append(core['flight'])
        GridFins.append(core['gridfins'])
        Reused.append(core['reused'])
        Legs.append(core['legs'])
        LandingPad.append(core['landpad'])


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


data = fetch_data()
processed_data = process_data(data)

try:
    os.makedirs(raw_data_directory, exist_ok=True)
    processed_data.to_csv(os.path.join(raw_data_directory, 'SpaceX_Falcon.csv'), index=False)
    logging.info("Dataset Saved as CSV")
except Exception as e:
    raise CustomExceptions(e, sys)




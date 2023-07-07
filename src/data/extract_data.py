import requests
import pandas as pd
import os
import datetime
from tqdm import tqdm
import sys
from api import SPACEX_URL, rockets, cores, launch_pad, payloads
import pytz

utc_now = datetime.datetime.now(pytz.utc)
america_timezone = pytz.timezone('America/New_York')
america_time = utc_now.astimezone(america_timezone)

year = america_time.year
month = america_time.month
day = america_time.day

response = requests.get(SPACEX_URL)

if response.status_code == 200:
    data = pd.json_normalize(response.json())

    data = data[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]
    data = data[data['cores'].map(len) == 1]
    data = data[data['payloads'].map(len) == 1]

    data['cores'] = data['cores'].map(lambda x: x[0])
    data['payloads'] = data['payloads'].map(lambda x: x[0])

    data['date'] = pd.to_datetime(data['date_utc']).dt.date

    data = data[data['date'] <= datetime.date(year, month, day)]

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


def getBoosterVersion(data):
    for x in tqdm(data['rocket'], desc='Fetching Booster Versions', bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
        response = requests.get(rockets + str(x)).json()
        BoosterVersion.append(response['name'])


def getLaunchSite(data):
    for x in tqdm(data['launchpad'], desc='Fetching Launch Sites', bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
        response = requests.get(launch_pad + str(x)).json()
        Longitude.append(response['longitude'])
        Latitude.append(response['latitude'])
        LaunchSite.append(response['name'])


def getPayloadData(data):
    for load in tqdm(data['payloads'], desc='Fetching Payload Data', bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
        response = requests.get(payloads + load).json()
        PayloadMass.append(response['mass_kg'])
        Orbit.append(response['orbit'])


def getCoreData(data):
    for core in tqdm(data['cores'], desc='Fetching Core Data', bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
        if core['core'] is not None:
            response = requests.get(cores + core['core']).json()
            Block.append(response['block'])
            ReusedCount.append(response['reuse_count'])
            Serial.append(response['serial'])
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


with tqdm(total=len(data['rocket']), desc='Fetching Data', bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
    getBoosterVersion(data)
    pbar.update(len(data['rocket']) - pbar.n)

with tqdm(total=len(data['launchpad']), desc='Fetching Data', bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
    getLaunchSite(data)
    pbar.update(len(data['launchpad']) - pbar.n)

with tqdm(total=len(data['payloads']), desc='Fetching Data', bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
    getPayloadData(data)
    pbar.update(len(data['payloads']) - pbar.n)

with tqdm(total=len(data['cores']), desc='Fetching Data', bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}') as pbar:
    getCoreData(data)
    pbar.update(len(data['cores']) - pbar.n)

launch_dict = {'FlightNumber': list(data['flight_number']),
               'Date': list(data['date']),
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

data = pd.DataFrame.from_dict(launch_dict)

output_directory = '/home/aditya/All Github/SpaceX/data/raw'
os.makedirs(output_directory, exist_ok=True)  # Create the directory if it doesn't exist

data.to_csv(os.path.join(output_directory, 'SpaceX_Falcon.csv'), index=False)

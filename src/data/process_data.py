import requests
import pandas as pd
from tqdm import tqdm
from src.api import rockets, launch_pad, payloads, cores
from src.utils.exception import CustomExceptions
import sys

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

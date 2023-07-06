import requests
import pandas as pd
import os
import datetime
from tqdm import tqdm
import sys
from src.utils.logger import logging
from src.utils.exception import CustomExceptions

from api import SPACEX_URL, rockets, cores, launch_pad, payloads


try:

    response = requests.get(SPACEX_URL)

    if response.status_code == 200:
        
        logging.info("Fetching Data from API")
        data=pd.json_normalize(response.json())
        
        data = data[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]
        data = data[data['cores'].map(len)==1]
        data = data[data['payloads'].map(len)==1]

        data['cores'] = data['cores'].map(lambda x : x[0])
        data['payloads'] = data['payloads'].map(lambda x : x[0])

        data['date'] = pd.to_datetime(data['date_utc']).dt.date

        data = data[data['date'] <= datetime.date(2020, 11, 13)]


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
    'BoosterVersion':BoosterVersion,
    'PayloadMass':PayloadMass,
    'Orbit':Orbit,
    'LaunchSite':LaunchSite,
    'Outcome':Outcome,
    'Flights':Flights,
    'GridFins':GridFins,
    'Reused':Reused,
    'Legs':Legs,
    'LandingPad':LandingPad,
    'Block':Block,
    'ReusedCount':ReusedCount,
    'Serial':Serial,
    'Longitude': Longitude,
    'Latitude': Latitude}

    data = pd.DataFrame.from_dict(launch_dict)

    logging.info("Converting Dataframe to Parquet")
    data.to_csv(os.path.join('data/raw', 'SpaceX_Falcon.csv'), index=False)

except Exception as e:
    raise CustomExceptions(e, sys)

#%%

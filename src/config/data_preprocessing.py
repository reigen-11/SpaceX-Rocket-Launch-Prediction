from src.utils.exception import CustomExceptions
from src.utils.logger import logging
import sys


def preprocess_data(data):
    try:
        df = data.copy()
        df = df.query("BoosterVersion == 'Falcon 9'").copy()

        df.loc[:, 'landing_location'] = df['Outcome'].apply(lambda x: str(x).split()[1])
        df.loc[:, 'Outcome'] = df['Outcome'].apply(lambda x: str(x).split()[0])
        df.loc[:, 'year'], df.loc[:, 'month'] = df['Date'].dt.year, df['Date'].dt.month
        df.loc[:, 'Outcome'] = df['Outcome'].replace({'None': 'False'})
        df['Outcome'] = df['Outcome'].apply(lambda x: True if x == 'True' else False)

        df = df.drop(['Serial', 'Block', 'BoosterVersion', 'FlightNumber', 'Date', 'Latitude', 'Longitude'],
                     axis=1).reset_index(drop=True)
        logging.info("Applied Basic Preprocessing And Data Cleaning to Data")
        return df

    except Exception as e:
        raise CustomExceptions(e, sys)

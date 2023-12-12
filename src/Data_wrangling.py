import logging
import os
from data.fetch_data import fetch_data
from data.process_data import process_data
from src.api import raw_data_directory
from utils.exception import CustomExceptions
import sys

data = fetch_data()
processed_data = process_data(data)

try:
    os.makedirs(raw_data_directory, exist_ok=True)
    processed_data.to_csv(os.path.join(raw_data_directory, 'SpaceX_Falcon.csv'), index=False)
    logging.info("Dataset Saved as CSV")
except Exception as e:
    raise CustomExceptions(e, sys)




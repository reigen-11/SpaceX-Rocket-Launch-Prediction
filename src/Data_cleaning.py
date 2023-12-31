import os
import sys
import pandas as pd
from dataclasses import dataclass
from logger import logging
from exception import CustomExceptions
from Data_transformation import preprocess_data
from api import preprocessed_data_dir, raw_data_csv

# print(sys.path)

@dataclass
class DataIngestionConfig:
    data_path: str = os.path.join(preprocessed_data_dir, "cleaned_data.csv")


class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info("Initiated Data Ingestion")
        try:

            df = pd.read_csv(raw_data_csv, parse_dates=['Date'])
            logging.info('Reading the dataset as dataframe')

            df = preprocess_data(df)
            df.to_csv(self.ingestion_config.data_path, index=False, header=True)
            logging.info("Data Ingestion Completed")

            return (
                self.ingestion_config.data_path,
            )
        except Exception as e:
            raise CustomExceptions(e, sys)


if __name__ == "__main__":
    obj = DataIngestion()
    cleaned_data_path = obj.initiate_data_ingestion()

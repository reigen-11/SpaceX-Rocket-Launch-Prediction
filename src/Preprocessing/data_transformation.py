import os
import sys
import pandas as pd
from dataclasses import dataclass
from src.utils.logger import logging
from src.data.api import transformed_data_dir, cleaned_data_csv
from src.utils.exception import CustomExceptions
from src.config.data_transformation import imputing_pipeline, encoding_pipeline, oversampling_pipeline


@dataclass
class DataTransformationConfig:
    transformed_data_path: str = os.path.join(transformed_data_dir, "transformed_df.csv")


class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def initiate_data_transformation(self):
        try:
            cleaned_df = pd.read_csv(cleaned_data_csv)
            imputed_df = imputing_pipeline(cleaned_df)
            encoded_df = encoding_pipeline(imputed_df)

            target_attribute = "Outcome"
            transformed_data = oversampling_pipeline(encoded_df.drop([target_attribute], axis=1),
                                                     encoded_df[target_attribute])
            logging.info(f"Transformed Data, Dataframe shape: {transformed_data.shape}")

            transformed_data.to_csv(self.data_transformation_config.transformed_data_path, index=False, header=True)
            logging.info(f"Saved Transformed Data as CSV")

            return self.data_transformation_config.transformed_data_path
        except Exception as e:
            error_message = f"Error in data transformation: {e}"
            logging.error(error_message)
            raise CustomExceptions(error_message, sys)


if __name__ == "__main__":
    obj = DataTransformation()
    transformed_df_path = obj.initiate_data_transformation()

import os
import sys
import pandas as pd
from dataclasses import dataclass
from src.utils.logger import logging
from src.utils.exception import CustomExceptions
from src.api import transformed_data_dir, cleaned_data_csv
from src.utils.data_transformation import imputing_pipeline, encoding_pipeline, oversampling_pipeline


@dataclass
class DataTransformationConfig:
    transformed_data_path: str = os.path.join(transformed_data_dir, "transformed_df.csv")


class DataTransformation:
    def __init__(self):
        self.data_transformation_config = DataTransformationConfig()

    def initiate_data_transformation(self):
        try:
            target_attribute = "Outcome"

            cleaned_df = pd.read_csv(cleaned_data_csv)
            imputed_df = imputing_pipeline(cleaned_df)
            category_cols = imputed_df.select_dtypes(include='object').columns
            encoded_df = encoding_pipeline(imputed_df, category_cols)
            input_features_arr, target_feature_arr, transformed_data = oversampling_pipeline(encoded_df.drop
                                                                                             ([target_attribute],
                                                                                              axis=1), encoded_df[
                                                                                                 target_attribute])
            logging.info(f"Transformed Data, Dataframe shape: {transformed_data.shape}")

            transformed_data.to_csv(self.data_transformation_config.transformed_data_path, index=False, header=True)
            logging.info(f"Saved Transformed Data as CSV")

            return input_features_arr, target_feature_arr, self.data_transformation_config.transformed_data_path

        except Exception as e:
            raise CustomExceptions(e, sys)

#
if __name__ == "__main__":
    obj = DataTransformation()
    input_features_arr, target_feature_arr, transformed_df_path = obj.initiate_data_transformation()

import os
import pickle
import sys
from dataclasses import dataclass

import pandas as pd
from imblearn.over_sampling import SMOTE
from pandas import DataFrame
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

from api import encoding_obj
from exception import CustomExceptions
from logger import logging
from api import transformed_data_dir, cleaned_data_csv


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


def imputing_pipeline(data: DataFrame) -> DataFrame:
    try:
        new_data = data.copy()
        original_dtypes = data.dtypes
        impute_step = ("impute", SimpleImputer(strategy="most_frequent"))
        data_impute_pipeline = Pipeline([impute_step])
        df_imputed = data_impute_pipeline.fit_transform(new_data)
        df_imputed = pd.DataFrame(df_imputed, columns=data.columns).astype(original_dtypes)

        logging.info("Data Imputed Successfully.")
        return df_imputed

    except Exception as e:
        raise CustomExceptions(e, sys)


def encoding_pipeline(data: DataFrame, cols: list) -> DataFrame:
    try:
        new_data = data.copy()

        data_encoding_pipeline = OrdinalEncoder()
        new_data[cols] = data_encoding_pipeline.fit_transform(new_data[cols])
        with open(encoding_obj, 'wb') as file:
            pickle.dump(data_encoding_pipeline, file)
        logging.info("Data Encoded Successfully.")
        return new_data

    except Exception as e:
        raise CustomExceptions(e, sys)


def oversampling_pipeline(X, y, sampling_strategy=0.5):
    try:
        data_oversampling_pipeline = SMOTE(sampling_strategy=sampling_strategy)
        X_resampled, y_resampled = data_oversampling_pipeline.fit_resample(X, y)
        resampled_df = pd.concat([X_resampled, y_resampled], axis=1)
        logging.info(f"Data Oversampled using SMOTE Successfully. "
                     f"Dataset Balanced with Target values {resampled_df['Outcome'].value_counts()} and Saved as CSV")

        return X_resampled, y_resampled, resampled_df

    except Exception as e:
        raise CustomExceptions(e, sys)


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

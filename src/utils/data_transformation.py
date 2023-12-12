from pandas import DataFrame
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
import pandas as pd
from src.utils.exception import CustomExceptions
import sys
import pickle
from src.utils.logger import logging
from src.api import encoding_obj


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

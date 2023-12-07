from pandas import DataFrame
from sklearn.preprocessing import OrdinalEncoder, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
import pandas as pd
from src.utils.exception import CustomExceptions
import sys
from src.utils.logger import logging


def imputing_pipeline(data: DataFrame) -> DataFrame:
    try:
        new_data = data.copy()

        impute_step = ("impute", SimpleImputer(strategy="most_frequent"))
        data_impute_pipeline = Pipeline([impute_step])
        df_imputed = data_impute_pipeline.fit_transform(new_data)
        df_imputed = pd.DataFrame(df_imputed, columns=data.columns)

        logging.info("Data Imputed Successfully.")
        return df_imputed

    except Exception as e:
        raise CustomExceptions(e, sys)


def encoding_pipeline(data: DataFrame) -> DataFrame:
    try:
        new_data = data.copy()

        encoding_step = ('encoding', OrdinalEncoder())
        data_encoding_pipeline = Pipeline([encoding_step])
        df_encoded = data_encoding_pipeline.fit_transform(new_data)
        df_encoded = pd.DataFrame(df_encoded, columns=data.columns)

        logging.info("Data Encoded Successfully.")
        return df_encoded

    except Exception as e:
        raise CustomExceptions(e, sys)


def oversampling_pipeline(X, y) -> DataFrame:
    try:
        data_oversampling_pipeline = SMOTE()
        X_resampled, y_resampled = data_oversampling_pipeline.fit_resample(X, y)
        resampled_df = pd.concat([X_resampled, y_resampled], axis=1)
        logging.info("Data Oversampled using SMOTE Successfully.")

        return resampled_df

    except Exception as e:
        raise CustomExceptions(e, sys)

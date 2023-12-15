import os
import sys
import pandas as pd
from api import ml_models_dir, transformed_data_csv, results, tuned_params_json
from exception import CustomExceptions
from logger import logging
from xgboost import XGBClassifier
from sklearn.metrics import classification_report
from dataclasses import dataclass
import pickle
from Hyperparameter_Tuning import calculate_average_score
from sklearn.model_selection import StratifiedKFold
import json


@dataclass
class ModelTrainerconfig:
    trained_model_path = os.path.join(ml_models_dir, "xgb_model.pkl")
    classification_reports_path: str = results
    tuned_hyperparams_path: str = tuned_params_json


class ModelTrainer:
    def __init__(self) -> None:
        self.model_trainer_config = ModelTrainerconfig()

    def load_tuned_hyperparams(self):
        try:
            with open(self.model_trainer_config.tuned_hyperparams_path, 'r') as file:
                tuned_hyperparams = json.load(file)
            logging.info(f"Loaded Tuned XGBoost Hyperparameters: {tuned_hyperparams}")
            return tuned_hyperparams
        except FileNotFoundError:
            logging.warning("Tuned hyperparameters file not found.")
            return None
        except json.decoder.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
            return None

    def init_model_training(self, input_features_array, target_features_array):
        try:
            tuned_hyperparams = self.load_tuned_hyperparams()

            if tuned_hyperparams is None:
                xgb_model = XGBClassifier()
            else:
                xgb_model = XGBClassifier(**tuned_hyperparams)

            # os.makedirs(os.path.dirname(self.model_trainer_config.trained_model_path), exist_ok=True)

            logging.info(f"Using XGBoost Classifier Model i.e. XGBOOST is all you need")

            skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            classification_reports = []

            for iteration, (train_index, test_index) in enumerate(
                    skf.split(input_features_array, target_features_array),
                    start=1):
                x_train_fold, x_test_fold = input_features_array.iloc[train_index], input_features_array.iloc[
                    test_index]
                y_train_fold, y_test_fold = target_features_array.iloc[train_index], target_features_array.iloc[
                    test_index]

                xgb_model.fit(x_train_fold, y_train_fold)
                y_predicted = xgb_model.predict(x_test_fold)
                report_dict = classification_report(y_test_fold, y_predicted, output_dict=True)
                logging.info(f"Iteration {iteration} : {report_dict}\n")
                classification_reports.append({f"Iteration {iteration}": report_dict})

            with open(self.model_trainer_config.classification_reports_path, 'w') as json_file:
                json.dump(classification_reports, json_file, indent=4)

            average_score = calculate_average_score(classification_reports)
            logging.info(f"Average Accuracy: {average_score}")

            with open(self.model_trainer_config.trained_model_path, 'wb') as f:
                pickle.dump(xgb_model, f)

            logging.info("Model trained and saved successfully. ")

            return self.model_trainer_config.trained_model_path

        except Exception as e:
            raise CustomExceptions(e, sys)


if __name__ == "__main__":
    df = pd.read_csv(transformed_data_csv)

    X = df.drop(columns=['Outcome'], axis=1)
    y = df['Outcome']
    train_model = ModelTrainer()
    model = train_model.init_model_training(X, y)

import json
import sys
from dataclasses import dataclass
import os
import numpy as np
import optuna
from sklearn.model_selection import cross_val_score
from xgboost import XGBClassifier
import pandas as pd
from exception import CustomExceptions
from api import transformed_data_csv, tuned_params_json


def calculate_average_score(classification_reports):
    accuracy_scores = [iteration["accuracy"] for report in classification_reports for iteration in report.values()]
    average_accuracy = sum(accuracy_scores) / len(accuracy_scores)
    return average_accuracy


def objective(trial, X, y):
    try:
        params = {
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'booster': 'gbtree',
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'n_estimators': trial.suggest_int('n_estimators', 100, 300),
        }

        model = XGBClassifier(**params)
        accuracy = np.mean(cross_val_score(model, X, y, cv=5, scoring='accuracy'))

        return accuracy

    except Exception as e:
        raise CustomExceptions(e, sys)


def tune_hyperparameters(features, target, n_trials: int):
    study = optuna.create_study(direction='maximize')
    objective_wrapper = lambda trial: objective(trial, features, target)
    study.optimize(objective_wrapper, n_trials=n_trials, n_jobs=-1)

    best_parameters = study.best_params

    return best_parameters


@dataclass
class hyperparameters_tuning_config:

    tuned_hyperparams_path: str = tuned_params_json


class hyperparameter_tuning:
    def __init__(self):
        self.param_tuning_config = hyperparameters_tuning_config()

    def save_tuned_hyperparams(self, tuned_hyperparams):
        with open(self.param_tuning_config.tuned_hyperparams_path, 'w') as file:
            json.dump(tuned_hyperparams, file, indent=4)


if __name__ == "__main__":
    df = pd.read_csv(transformed_data_csv)

    X = df.drop(columns=['Outcome'], axis=1)
    y = df['Outcome']

    tuner = hyperparameter_tuning()
    n_trials = 50
    best_params = tune_hyperparameters(X, y, n_trials)
    tuner.save_tuned_hyperparams(best_params)

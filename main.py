from src.data_clean import DataIngestion
from src.data_transform import DataTransformation
from src.Data_wrangling import main
from src.hyperparam_tuning import hyperparameter_tuning, tune_hyperparameters
from src.train import ModelTrainer


def main_workflow():
    main()

    # Data Ingestion
    data_ingestion = DataIngestion()
    cleaned_data_path = data_ingestion.initiate_data_ingestion()

    # Data Transformation
    data_transformation = DataTransformation()
    input_features_arr, target_feature_arr, transformed_df_path = data_transformation.initiate_data_transformation()

    # Hyperparameter Tuning
    tuner = hyperparameter_tuning()
    n_trials = 50
    best_params = tune_hyperparameters(input_features_arr, target_feature_arr, n_trials)
    tuner.save_tuned_hyperparams(best_params)

    # Model Training
    model_trainer = ModelTrainer()
    model = model_trainer.init_model_training(input_features_arr, target_feature_arr)


if __name__ == "__main__":
    main_workflow()

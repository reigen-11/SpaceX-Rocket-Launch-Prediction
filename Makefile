init:
	@echo "Checking if virtual environment exists..."
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv venv; \
	fi
	@echo "Activating virtual environment..."
	@. venv/bin/activate; \
	echo "Virtual environment activated."

.PHONY: init


install_dependencies:
	pip install -r requirements.txt

update_requirements:
	pipreqs . --force

fetch_data:
	python src/Data_wrangling.py

clean_data:
	python src/Data_cleaning.py

encode_data:
	python src/Data_transformation.py

tune_hyperparams:
	python src/Hyperparameter_Tuning.py

train:
	python src/Train_model.py

app:
	export FLASK_APP=app.py
	flask run






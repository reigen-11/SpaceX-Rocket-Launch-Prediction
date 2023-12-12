install_dependencies:
	pip install -r requirements.txt

update_requirements:
	pipreqs . --force

clean_data:
	python src/data_clean.py

data_transform:
	python src/data_transform.py

train:
	python src/train.py

app:
	streamlit run app.py






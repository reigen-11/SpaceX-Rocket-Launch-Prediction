fetch_data:
	python data/main.py

install:
	pip install -r requirements.txt

update_reqs:
	pipreqs . --force
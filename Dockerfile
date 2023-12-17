FROM python:3.11.7
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
CMD gunicorn --workers=4 --bind 0.0.0.0:5000 app:app

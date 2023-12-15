from flask import Flask, render_template, request
import pandas as pd
import pickle
from src.api import cleaned_data_csv

app = Flask(__name__)

with open("/home/aditya/All Github/SpaceX/models/xgb_model.pkl", "rb") as model_file:
    xgb = pickle.load(model_file)

with open('/home/aditya/All Github/SpaceX/artifacts/data_encoding_object.pkl', 'rb') as file:
    encoder = pickle.load(file)

df = pd.read_csv(cleaned_data_csv)


def get_dropdown_data():
    orbit_list = df['Orbit'].dropna().unique().tolist()
    launch_site_list = df['LaunchSite'].dropna().unique().tolist()
    landing_pad_list = df['LandingPad'].dropna().unique().tolist()
    landing_location_list = df['landing_location'].dropna().unique().tolist()

    return orbit_list, launch_site_list, landing_pad_list, landing_location_list


def predict_outcome(input_data):
    input_df = pd.DataFrame([input_data])
    input_df[['Orbit', 'LaunchSite', 'LandingPad', 'landing_location']] = encoder.transform(
        input_df[['Orbit', 'LaunchSite', 'LandingPad', 'landing_location']])
    prediction = xgb.predict(input_df)
    probability = xgb.predict_proba(input_df)
    return prediction, probability


@app.route('/')
def index():
    orbit, launch, landing, landing_loc = get_dropdown_data()
    return render_template('index.html', orbit_list=orbit, launch_site_list=launch,
                           landing_pad_list=landing, landing_location_list=landing_loc)


@app.route('/result', methods=['POST'])
def predict():
    if request.method == 'POST':
        payload_mass = float(request.form['payload_mass'])
        orbit = request.form['orbit']
        launch_site = request.form['launch_site']
        flights = int(request.form['flights'])
        grid_fins = bool(request.form.get('grid_fins'))
        reused = bool(request.form.get('reused'))
        legs = bool(request.form.get('legs'))
        landing_pad = request.form['landing_pad']
        reused_count = int(request.form['reused_count'])
        landing_location = request.form['landing_location']
        year = int(request.form['year'])
        month = int(request.form['month'])

        input_data = {
            "PayloadMass": payload_mass,
            "Orbit": orbit,
            "LaunchSite": launch_site,
            "Flights": flights,
            "GridFins": grid_fins,
            "Reused": reused,
            "Legs": legs,
            "LandingPad": landing_pad,
            "ReusedCount": reused_count,
            "landing_location": landing_location,
            "year": year,
            "month": month,
        }

        prediction, probability = predict_outcome(input_data)

        return render_template('result.html', prediction=prediction, probability=probability, result=bool(prediction))

if __name__ == "__main__":
    app.run(debug=True)

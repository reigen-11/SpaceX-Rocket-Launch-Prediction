import streamlit as st
import pandas as pd
import pickle
import time
import seaborn as sns
import matplotlib.pyplot as plt
st.set_option('deprecation.showPyplotGlobalUse', False)

with open("/home/aditya/All Github/SpaceX/models/xgb_model.pkl", "rb") as model_file:
    xgb = pickle.load(model_file)

with open('/home/aditya/All Github/SpaceX/artifacts/data_encoding_object.pkl', 'rb') as file:
    encoder = pickle.load(file)


def display_rocket_animation():
    rocket_gif_path = "templates/booster.gif"
    st.image(rocket_gif_path)


def predict_outcome(input_data):
    input_df = pd.DataFrame([input_data])
    input_df[['Orbit', 'LaunchSite', 'LandingPad', 'landing_location']] = encoder.transform(
        input_df[['Orbit', 'LaunchSite', 'LandingPad', 'landing_location']])
    prediction = xgb.predict(input_df)
    probability = xgb.predict_proba(input_df)
    return prediction, probability


def main():

    df = pd.read_csv("/home/aditya/All Github/SpaceX/artifacts/data/processed/cleaned_data.csv")
    st.title("SpaceX Launch Outcome Predictor")

    payload_mass = st.number_input("PayloadMass in Kg of the Rocket Carrying", min_value=0)

    orbit_options = df['Orbit'].dropna().unique().tolist()
    orbit = st.selectbox("Orbit in Which The Rocket will Enter", orbit_options) if orbit_options \
        else st.error("Please select a valid Orbit.")

    launch_site_options = df['LaunchSite'].dropna().unique().tolist()
    launch_site = st.selectbox("Launch Site", launch_site_options) if launch_site_options \
        else st.error("Please select a valid Launch Site.")

    flights = st.number_input("Flights", min_value=0)
    grid_fins = st.checkbox("Grid Fins")
    reused = st.checkbox("Reused")
    legs = st.checkbox("Legs")

    landing_pad_options = df['LandingPad'].dropna().unique().tolist()
    landing_pad = st.selectbox("Landing Pad", landing_pad_options) if landing_pad_options \
        else st.error("Please select a valid Landing Pad.")

    reused_count = st.number_input("Reused Count", min_value=0, max_value=20)

    landing_location_options = df['landing_location'].dropna().unique().tolist()
    landing_location = st.selectbox("Landing Location", landing_location_options) if landing_location_options \
        else st.error("Please select a valid Landing Location.")

    year = st.number_input("Year", min_value=2000, max_value=2030, value=2022)
    month = st.number_input("Month", min_value=1, max_value=12, value=1)

    if st.button("Predict Outcome"):
        with st.spinner(f"{display_rocket_animation()}"):
            time.sleep(5)

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
            st.success(f"According to Historical Data Probability that the Rocket will Launch is : {bool(prediction)}\n"
                       f"\nLaunch Success Probability : {probability[0][1]}  "
                       f"\nLaunch Failure Probability : {probability[0][0]}")

            st.subheader("Launch Success Probability Distribution")

            fig, ax = plt.subplots()

            x_order = ["Launch Failure", "Launch Success"]

            sns.barplot(x=x_order, y=probability[0], hue=x_order,
                        palette="viridis", ax=ax, dodge=False, legend=False)

            for p in ax.patches:
                height = p.get_height()
                ax.text(p.get_x() + p.get_width() / 2., height + 0.01, f'{height * 100:.1f}%', ha="center",
                        fontsize=12, color='black')

            st.pyplot(fig)


if __name__ == "__main__":
    main()

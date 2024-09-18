#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import folium
from streamlit_folium import folium_static

# Load data from your specific file path
data_file = r'D:/Sudardeva/Watch Hackathon/AQI_fill.csv'

# Streamlit app layout
st.title("AQI Monitoring Tool")

# Map Feature for NIT Warangal
latitude = 17.9836  # Updated Latitude for NIT Warangal
longitude = 79.5308  # Updated Longitude for NIT Warangal

# Create a map centered around NIT Warangal
m = folium.Map(location=[latitude, longitude], zoom_start=15)

# Add a marker for the monitoring station
folium.Marker([latitude, longitude], tooltip='NIT Warangal Monitoring Station').add_to(m)

# Display the map in the Streamlit app
st.write("### AQI Monitoring Stations NIT Warangal")
folium_static(m)

# Read the file using the correct delimiter (comma)
data = pd.read_csv(data_file, delimiter=',')  # Ensure delimiter is correct
data.columns = data.columns.str.strip()  # Clean column names

# Display the first few rows and column names for debugging
st.write("### Data Preview")
st.write(data.head())
st.write("Columns:", data.columns.tolist())

# Check if 'timestamp' and 'AQIH' exist in the columns
if 'timestamp' not in data.columns or 'AQIH' not in data.columns:
    st.error("Required columns 'timestamp' or 'AQIH' not found in the data.")
else:
    # Parse dates
    data['timestamp'] = pd.to_datetime(data['timestamp'], format='%d-%m-%y %H:%M')

    # Function to calculate statistics
    def calculate_statistics(df):
        return {
            'Average AQI': df['AQIH'].mean(),
            'Max AQI': df['AQIH'].max(),
            'Min AQI': df['AQIH'].min(),
        }

    # Function to plot AQI over time
    def plot_aqi(df):
        plt.figure(figsize=(10, 5))
        plt.plot(df['timestamp'], df['AQIH'], marker='o', label='AQI (15 min intervals)')
        plt.title('AQI Over Time')
        plt.xlabel('Timestamp')
        plt.ylabel('AQI')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt)

    # Function to analyze hourly averages and suggest general no-go times
    def analyze_hourly_aqi(df):
        df.set_index('timestamp', inplace=True)
        hourly_avg = df.resample('H').mean()
        high_aqi_times = hourly_avg[hourly_avg['AQIH'] > 150]

        return high_aqi_times.index.hour.value_counts().sort_index()

    # Function to plot high AQI counts
    def plot_high_aqi_counts(high_aqi_counts):
        plt.figure(figsize=(12, 6))
        high_aqi_counts.plot(kind='bar', color='red')
        plt.title('Hourly High AQI Counts')
        plt.xlabel('Hour of Day')
        plt.ylabel('Count of High AQI Readings')
        plt.xticks(rotation=0)
        plt.tight_layout()
        st.pyplot(plt)

    # Health tips based on AQI levels
    def health_tips(aqi):
        if aqi <= 50:
            return "Air quality is satisfactory; air pollution poses little or no risk."
        elif aqi <= 100:
            return "Air quality is acceptable; however, some pollutants may be a concern for a small number of people."
        elif aqi <= 150:
            return "Members of sensitive groups may experience health effects. The general public is less likely to be affected."
        elif aqi <= 200:
            return "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects."
        elif aqi <= 300:
            return "Health alert: everyone may experience more serious health effects."
        else:
            return "Health warnings of emergency conditions. The entire population is more likely to be affected."

    # Function to generate risk levels based on high AQI counts
    def generate_hourly_risk_levels(high_aqi_counts):
        risk_levels = []
        
        for hour in range(24):
            count = high_aqi_counts.get(hour, 0)  # Default to 0 if no high AQI data for the hour
            if count <= 2:
                risk_levels.append(f"During {hour}:00 - {hour}:59, risk level is Low. Outdoor activities are generally safe.")
            elif count <= 5:
                risk_levels.append(f"During {hour}:00 - {hour}:59, risk level is Moderate. Consider limiting outdoor activities.")
            elif count <= 10:
                risk_levels.append(f"During {hour}:00 - {hour}:59, risk level is High. Avoid strenuous outdoor activities.")
            else:
                risk_levels.append(f"During {hour}:00 - {hour}:59, risk level is Very High. Stay indoors as much as possible.")

        return risk_levels

    # Function to plot risk levels
    def plot_risk_levels(risk_levels):
        hours = [f"{hour}:00" for hour in range(24)]
        risk_values = [1 if "Low" in level else 2 if "Moderate" in level else 3 if "High" in level else 4 for level in risk_levels]
        
        plt.figure(figsize=(12, 6))
        plt.bar(hours, risk_values, color='orange')
        plt.title('Hourly Risk Levels Based on AQI Counts')
        plt.xlabel('Hour of Day')
        plt.ylabel('Risk Level (1-Low to 4-Very High)')
        plt.xticks(rotation=45)
        plt.ylim(0, 5)  # Set y-axis limit for better visualization
        plt.grid(axis='y')
        st.pyplot(plt)

    # AQI Statistics Section
    st.write("### AQI Statistics")
    stats = calculate_statistics(data)
    for key, value in stats.items():
        st.write(f"{key}: {value}")

    st.write("### AQI Over Time (15 Min Intervals)")
    plot_aqi(data)

    # Analyze and plot high AQI counts
    high_aqi_counts = analyze_hourly_aqi(data)
    if not high_aqi_counts.empty:
        plot_high_aqi_counts(high_aqi_counts)
        
        # Risk Levels Section
        st.write("### Risk Levels Based on Hourly High AQI Counts")
        risk_levels = generate_hourly_risk_levels(high_aqi_counts)
        for risk in risk_levels:
            st.write(f"- {risk}")

        # Plotting the risk levels chart
        plot_risk_levels(risk_levels)
    else:
        st.write("Air quality is generally safe throughout the day.")

    # Health Tips Section
    st.write("### Health Tips Based on AQI Levels")
    aqi_value = st.number_input("Enter an AQI value to get health tips:", min_value=0, value=0)
    if aqi_value is not None:
        st.write(health_tips(aqi_value))



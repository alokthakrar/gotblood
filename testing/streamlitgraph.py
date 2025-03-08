import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Sample Data with Latitude and Longitude (PLACEHOLDER COORDINATES - REPLACE WITH REAL DATA)
data = {
    'Hospital': ['Hospital A', 'Hospital A', 'Hospital A', 'Hospital B', 'Hospital B', 'Hospital B', 'Hospital C', 'Hospital C', 'Hospital C', 'Hospital A', 'Hospital B', 'Hospital C'],
    'Blood Type': ['A+', 'B+', 'O+', 'A+', 'B+', 'O+', 'A+', 'B+', 'O+', 'AB-', 'AB-', 'AB-'],
    'Amount': [15, 8, 22, 10, 18, 30, 5, 12, 25, 3, 7, 11],
    'Latitude': [34.0522, 34.0522, 34.0522, 40.7128, 40.7128, 40.7128, 37.7749, 37.7749, 37.7749, 34.0522, 40.7128, 37.7749], # Los Angeles, New York City, San Francisco (Placeholder)
    'Longitude': [-118.2437, -118.2437, -118.2437, -74.0060, -74.0060, -74.0060, -122.4194, -122.4194, -122.4194, -118.2437, -74.0060, -122.4194] # Los Angeles, New York City, San Francisco (Placeholder)
}
df = pd.DataFrame(data)

st.title("Blood Bank Inventory Visualization on US Map")
st.write("Visualizing blood inventory across different hospitals in the US.")

st.subheader("Raw Data")
st.dataframe(df)

st.subheader("Blood Inventory Map")

# 1. Prepare Data (No need for hospital/blood type indices anymore for map)

# 2. Create the Scattergeo plot
fig = go.Figure(data=go.Scattergeo(
    lon=df['Longitude'],
    lat=df['Latitude'],
    mode='markers',
    marker=dict(
        size=df['Amount'] * 1.5,  # Adjust scaling factor for marker size
        color=df['Amount'],
        colorscale='Viridis',
        opacity=0.8,
        colorbar=dict(title='Blood Amount')
    ),
    text=[f"Hospital: {h}<br>Blood Type: {bt}<br>Amount: {a}" for h, bt, a in zip(df['Hospital'], df['Blood Type'], df['Amount'])],
    hoverinfo='text'
))

# 3. Customize Layout for Geo Map
fig.update_layout(
    geo=dict(
        scope='usa',  # Focus on the USA
        projection_scale=3, # Adjust for zoom level, larger is closer zoom
        center=dict(lat=39.8283, lon=-98.5795), # Center of USA roughly
        landcolor="lightgray",
        countrycolor="black",
        coastlinecolor="black",
    ),
    title_text='Blood Inventory by Hospital Location and Blood Type',
    margin=dict(l=0, r=0, b=0, t=50)
)

st.plotly_chart(fig)
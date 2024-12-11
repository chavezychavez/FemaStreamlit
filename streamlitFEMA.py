import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# Title for the dashboard
st.title("FEMA Active and Recently Closed Disasters Dashboard")
#st.set_page_config(layout='wide')

# Step 1: Fetch FEMA Web Disaster Declarations API Data
@st.cache_data
def fetch_fema_web_data():
    url = "https://www.fema.gov/api/open/v1/FemaWebDisasterDeclarations?$orderby=disasterNumber%20desc"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['FemaWebDisasterDeclarations']
    else:
        st.error("Failed to retrieve data from FEMA API")
        return []

# Step 2: Process the data
data = fetch_fema_web_data()

# Convert to a DataFrame
df = pd.DataFrame(data)

# Convert date columns to datetime
df['incidentBeginDate'] = pd.to_datetime(df['incidentBeginDate'])
df['incidentEndDate'] = pd.to_datetime(df['incidentEndDate'], errors='coerce')  # Convert nulls to NaT

# Remove timezone information for comparison
df['incidentBeginDate'] = df['incidentBeginDate'].dt.tz_localize(None)

# Step 3: Filter Active Disasters (incidentEndDate is null)
active_disasters = df[df['incidentEndDate'].isnull()]

# Step 4: Filter Recently Closed Disasters (incidentBeginDate >= current date - 90 days and incidentEndDate not null)
current_date = datetime.now()
last_90_days = current_date - timedelta(days=90)
recently_closed_disasters = df[(df['incidentBeginDate'] >= last_90_days) & (df['incidentEndDate'].notnull())]

# Step 5: Display Active Disasters
st.subheader("Active Disasters")
st.write(f"Number of Active Disasters: {active_disasters.shape[0]}")
st.dataframe(active_disasters[['disasterName', 'stateCode', 'stateName', 'declarationDate', 'incidentBeginDate', 'incidentEndDate', 'incidentType']])

# Step 6: Display Recently Closed Disasters
st.subheader("Disasters Closed in the Last 90 Days")
st.write(f"Number of Recently Closed Disasters: {recently_closed_disasters.shape[0]}")
st.dataframe(recently_closed_disasters[['disasterName', 'stateCode', 'stateName', 'declarationDate', 'incidentBeginDate', 'incidentEndDate', 'incidentType']])

# Step 7: Visualize Active Disasters by State
st.subheader("Active Disasters by State")
active_disasters_by_state = active_disasters.groupby('stateCode').size().reset_index(name='counts')

bar_chart_active = alt.Chart(active_disasters_by_state).mark_bar().encode(
    x='stateCode',
    y='counts',
    color='stateCode'
)

st.altair_chart(bar_chart_active, use_container_width=True)

# Step 8: Visualize Recently Closed Disasters by State
st.subheader("Recently Closed Disasters by State")
recently_closed_by_state = recently_closed_disasters.groupby('stateCode').size().reset_index(name='counts')

bar_chart_closed = alt.Chart(recently_closed_by_state).mark_bar().encode(
    x='stateCode',
    y='counts',
    color='stateCode'
)

st.altair_chart(bar_chart_closed, use_container_width=True)

# Step 9: Incident Type Distribution for Active Disasters
st.subheader("Active Disasters by Incident Type")
active_by_type = active_disasters.groupby('incidentType').size().reset_index(name='counts')

pie_chart_active_type = alt.Chart(active_by_type).mark_arc().encode(
    theta='counts',
    color='incidentType',
    tooltip=['incidentType', 'counts']
)

st.altair_chart(pie_chart_active_type, use_container_width=True)

# Step 10: Incident Type Distribution for Recently Closed Disasters
st.subheader("Recently Closed Disasters by Incident Type")
closed_by_type = recently_closed_disasters.groupby('incidentType').size().reset_index(name='counts')

pie_chart_closed_type = alt.Chart(closed_by_type).mark_arc().encode(
    theta='counts',
    color='incidentType',
    tooltip=['incidentType', 'counts']
)

st.altair_chart(pie_chart_closed_type, use_container_width=True)

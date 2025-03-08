import streamlit as st

st.title("Hospital Blood Availability Tracker")

st.sidebar.header("Filter Hospitals")
blood_filter = st.sidebar.selectbox(
    "Choose blood type:",
    ["All", "A", "B", "O", "AB"]
)

# Display some UI components
st.write("Map displaying hospitals with blood availability will go here.")
st.write(f"Currently showing hospitals with blood type: {blood_filter}")

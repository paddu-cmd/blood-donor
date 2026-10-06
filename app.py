import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st

# Force sidebar pink, main area white
st.markdown(
    """
    <style>
    /* Sidebar (left side) */
    [data-testid="stSidebar"] {
        background-color: #ffe6f0; /* baby pink */
    }
    [data-testid="stSidebar"] * {
        color: #333333; /* readable dark text */
    }

    /* Main content (right side) */
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff; /* white */
    }

    /* Headers */
    h1, h2, h3 {
        color: #ff66b2;
    }

    /* Buttons */
    .stButton>button {
        background-color: #ff99cc;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #ff66b2;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --- Database Setup ---
conn = sqlite3.connect("blood_donor.db", check_same_thread=False)
c = conn.cursor()

# Create tables if not exist
c.execute('''CREATE TABLE IF NOT EXISTS donors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    blood_group TEXT,
    contact TEXT,
    location TEXT,
    availability TEXT,
    donations INTEGER DEFAULT 0,
    response_history INTEGER DEFAULT 100
)''')

c.execute('''CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    blood_group TEXT,
    units INTEGER,
    urgency TEXT,
    hospital TEXT,
    req_date TEXT,
    req_time TEXT,
    location TEXT,
    contact TEXT,
    status TEXT DEFAULT 'Pending'
)''')

conn.commit()

# --- Sidebar Navigation ---
module = st.sidebar.radio("Navigate", [
    "Donor Module",
    "Emergency Request Module",
    "Smart Matching Module",
    "Hospital/Admin Module"
])

# --- Donor Module ---
if module == "Donor Module":
    st.header("Donor Module")
    with st.form("donor_form"):
        name = st.text_input("Name")
        blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        contact = st.text_input("Contact Information")
        location = st.text_input("Location")
        availability = st.radio("Availability Status", ["Available", "Unavailable"])
        submitted = st.form_submit_button("Register / Update Profile")
    if submitted:
        c.execute("INSERT INTO donors (name, blood_group, contact, location, availability) VALUES (?, ?, ?, ?, ?)",
                  (name, blood_group, contact, location, availability))
        conn.commit()
        st.success(f"Donor {name} registered with {blood_group}")

    st.subheader("Donation History")
    donors = pd.read_sql("SELECT * FROM donors", conn)
    st.dataframe(donors)

# --- Emergency Request Module ---
elif module == "Emergency Request Module":
    st.header("Emergency Request Module")
    with st.form("request_form"):
        req_blood = st.selectbox("Required Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        units = st.number_input("Units Required", min_value=1, max_value=10)
        urgency = st.selectbox("Emergency Level", ["High", "Medium", "Low"])
        hospital = st.text_input("Hospital / Blood Bank Information")
        req_date = st.date_input("Required Date")
        req_time = st.time_input("Required Time")
        location = st.text_input("Location")
        contact = st.text_input("Contact Information")
        submitted = st.form_submit_button("Submit Request")
    if submitted:
        c.execute("INSERT INTO requests (blood_group, units, urgency, hospital, req_date, req_time, location, contact) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (req_blood, units, urgency, hospital, str(req_date), str(req_time), location, contact))
        conn.commit()
        st.success(f"Request submitted for {units} units of {req_blood}")

    st.subheader("Active Requests")
    requests = pd.read_sql("SELECT * FROM requests", conn)
    st.dataframe(requests)

# --- Smart Matching Module ---
elif module == "Smart Matching Module":
    st.header("Smart Matching Module")
    requests = pd.read_sql("SELECT * FROM requests WHERE status='Pending'", conn)
    donors = pd.read_sql("SELECT * FROM donors WHERE availability='Available'", conn)

    if not requests.empty and not donors.empty:
        st.write("Pending Requests:", requests)
        st.write("Available Donors:", donors)

        # Simple ranking: by donations + response_history
        ranked = donors.sort_values(by=["response_history", "donations"], ascending=False)
        st.subheader("Ranked Donors")
        st.dataframe(ranked)
    else:
        st.info("No pending requests or available donors.")



# --- Hospital/Admin Module ---
elif module == "Hospital/Admin Module":
    st.header("Hospital / Admin Module")
    admin_action = st.selectbox("Choose Action", [
        "Create & Manage Requests",
        "Verify Requests",
        "View Matched Donors",
        "Monitor Active Emergencies",
        "Manage Donor Records",
        "Track Completed Requests",
        "Detect Duplicate/Fraudulent Requests"
    ])

    if admin_action == "Create & Manage Requests":
        st.write("Admin can create or update requests here.")
    elif admin_action == "Verify Requests":
        st.write("Admin verifies pending requests.")
    elif admin_action == "View Matched Donors":
        st.write("Admin views donor matches for requests.")
    elif admin_action == "Monitor Active Emergencies":
        st.write("Admin monitors ongoing emergencies.")
    elif admin_action == "Manage Donor Records":
        donors = pd.read_sql("SELECT * FROM donors", conn)
        st.dataframe(donors)
    elif admin_action == "Track Completed Requests":
        completed = pd.read_sql("SELECT * FROM requests WHERE status='Completed'", conn)
        st.dataframe(completed)
    elif admin_action == "Detect Duplicate/Fraudulent Requests":
        st.write("Admin checks for duplicate/fraudulent requests.")

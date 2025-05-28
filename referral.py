import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Database setup
conn = sqlite3.connect("mtrh.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    creation_date TEXT,
    diagnosis_date TEXT,
    diagnosis TEXT,
    healthcare_service_unit TEXT,
    patient_id TEXT,
    mobile_number TEXT,
    gender TEXT,
    age INTEGER
)
""")
conn.commit()

clinic_names = [
    "S4A OPD Ambulatory", "PW 2 OPD - Consultant Room - MTRH",
    "Ambulatory Consultation - MTRH", "ED - Medical Emergency (Rm 14) - MTRH",
    "Diabetic Clinic - Chandaria - MTRH", "ENT - General - MTRH",
    "Haematology Clinic - Chandaria - MTRH", "MOPC CLINIC - MTRH",
    "Dental- OMFS- Oral & Maxillofacial Clinic - MTRH", "General-Oncology Telemedicine - MTRH"
]

st.title("🏥 MTRH Healthcare System")

# Tabs for operations
tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Patient", "🔍 View Patient", "❌ Delete Patient", "⬇️ Download Data"])

# Add Patient
with tab1:
    st.header("Register New Patient")
    with st.form("add_patient_form"):
        patient_id = st.text_input("Patient ID")
        diagnosis = st.text_input("Diagnosis")
        healthcare_unit = st.selectbox("Healthcare Service Unit", clinic_names)
        mobile_number = st.text_input("Mobile Number")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.number_input("Age", min_value=0, max_value=120)
        submitted = st.form_submit_button("Submit")

        if submitted:
            if not all([diagnosis, healthcare_unit, patient_id, mobile_number, gender, age]):
                st.warning("All fields must be filled!")
            else:
                creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                diagnosis_date = creation_date
                data = (creation_date, diagnosis_date, diagnosis, healthcare_unit, patient_id, mobile_number, gender, age)
                cursor.execute("INSERT INTO patients (creation_date, diagnosis_date, diagnosis, healthcare_service_unit, patient_id, mobile_number, gender, age) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
                conn.commit()
                st.success("✅ Patient data saved successfully!")

# View Patient
with tab2:
    st.header("View Patient Record")
    pid = st.text_input("Enter Patient ID to Search", key="view_pid")
    if st.button("Search"):
        if not pid:
            st.warning("Please enter a Patient ID.")
        else:
            cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (pid,))
            record = cursor.fetchone()
            if record:
                st.markdown(f"""
                **📌 ID:** {record[0]}  
                **📅 Creation Date:** {record[1]}  
                **🗓️ Diagnosis Date:** {record[2]}  
                **💉 Diagnosis:** {record[3]}  
                **🏥 Healthcare Unit:** {record[4]}  
                **🆔 Patient ID:** {record[5]}  
                **📞 Mobile Number:** {record[6]}  
                **⚧ Gender:** {record[7]}  
                **🎂 Age:** {record[8]}
                """)
            else:
                st.error("❌ No record found for the given Patient ID.")

# Delete Patient
with tab3:
    st.header("Delete Patient Record")
    pid_del = st.text_input("Enter Patient ID to Delete", key="delete_pid")
    if st.button("Delete"):
        if not pid_del:
            st.warning("Please enter a Patient ID.")
        else:
            cursor.execute("DELETE FROM patients WHERE patient_id = ?", (pid_del,))
            conn.commit()
            st.success("✅ Record deleted successfully!")

# Download Data
with tab4:
    st.header("Download All Patient Data")
    if st.button("Download as CSV"):
        cursor.execute("SELECT * FROM patients")
        records = cursor.fetchall()
        if records:
            columns = ["ID", "Creation Date", "Diagnosis Date", "Diagnosis", "Healthcare Unit", "Patient ID", "Mobile", "Gender", "Age"]
            df = pd.DataFrame(records, columns=columns)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Click to Download", csv, file_name='mtrh_data.csv', mime='text/csv')
        else:
            st.warning("No records found to download.")

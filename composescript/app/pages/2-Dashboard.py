import os
import streamlit as st
import oracledb
import pandas as pd
from dotenv import load_dotenv

# **🔹 Load environment variables**
load_dotenv()

st.set_page_config(page_title="📈 Loan Officer Dashboard", layout="wide")
st.title("📈 Loan Officer Dashboard")
st.info("View available loan requests, visualize loan scoring, and explore top loan options.")

# **🔹 Database Connection**
DB_USER = os.getenv("USERNAME")
DB_PASSWORD = os.getenv("DBPASSWORD")
DB_DSN = os.getenv("DBCONNECTION")

def get_db_connection():
    try:
        return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

conn = get_db_connection()
if not conn:
    st.stop()

cursor = conn.cursor()

# **🔹 Function to Fetch Customer Data by Status**
def fetch_customers_by_status(status):
    cursor.execute(f"""
        SELECT 
            JSON_VALUE(data, '$._id') AS customer_id,
            JSON_VALUE(data, '$.first_name') AS first_name,
            JSON_VALUE(data, '$.last_name') AS last_name,
            JSON_VALUE(data, '$.application_id') AS application_id,
            JSON_VALUE(data, '$.requested_loan_amount' RETURNING NUMBER) AS requested_loan_amount,
            JSON_VALUE(data, '$.loan_status') AS loan_status
        FROM clients_dv
        WHERE JSON_VALUE(data, '$.loan_status') = :status
    """, status=status)

    return [
        {
            "Customer ID": row[0],
            "First Name": row[1],
            "Last Name": row[2],
            "Application ID": row[3],
            "Requested Loan Amount": row[4],
            "Loan Status": row[5]
        }
        for row in cursor.fetchall()
    ]

# **🔹 Fetch Customers by Status**
pending_customers = fetch_customers_by_status('Pending Review')
approved_customers = fetch_customers_by_status('Approved')
denied_customers = fetch_customers_by_status('Denied')

# **🔹 Function to Display DataFrames in Streamlit**
def display_customers_table(customers, status_label, emoji):
    df = pd.DataFrame(customers)
    
    if not df.empty:
        df["Customer ID"] = df["Customer ID"].apply(
            lambda customer_id: f'<a href="/customers?customer_id={customer_id}" target="_self">{customer_id}</a>'
        )
        st.subheader(f"{emoji} {status_label} Loan Requests")
        st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.warning(f"No {status_label.lower()} loan requests available for display.")

# **🔹 Display Tables for Each Loan Status**
display_customers_table(pending_customers, "Pending Review", "📋")
display_customers_table(approved_customers, "Approved", "✅")
display_customers_table(denied_customers, "Denied", "❌")

# **🔹 Clean Up**
cursor.close()
conn.close()
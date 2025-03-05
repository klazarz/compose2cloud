import streamlit as st

# Page Configuration
st.set_page_config(page_title="AI-Powered Loan Approval System", layout="wide")

# App Title
st.title("🏦 AI-Powered Loan Approval & Wealth Management System")

# Introduction Section
st.markdown(
    """
    ## 📌 Project Overview
    Welcome to the AI-Powered Loan Officer Platform! This system leverages **Oracle 23AI, AI Vector Search, JSON Duality Views, and Operational Property Graphs** to streamline loan approvals and financial risk assessment.

    ### 🔹 Key Features:
    - **AI-Driven Loan Approval**: Automated decision-making based on financial data.
    - **Risk Assessment**: AI evaluates credit risk and financial health.
    - **Graph-Based Wealth Management**: Visualize customer loans, investments, and debts.
    - **RAG-Based AI Assistance**: Ask AI-powered questions like *"Why was the loan denied?"*.
    - **Document Processing**: Upload and analyze financial documents.

    Use the navigation on the left to explore the system.
    """,
    unsafe_allow_html=True,
)

# Sidebar Navigation Info
st.sidebar.success("Select a page from the sidebar to get started.")

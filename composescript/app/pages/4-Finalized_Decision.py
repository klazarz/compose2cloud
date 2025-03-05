import os
import streamlit as st
from fpdf import FPDF
import json
import oracledb

st.set_page_config(page_title="📄 Finalized Decision", layout="wide")
st.title("📄 Finalized Decision Page")

# 🔹 Retrieve stored session data
customer_first_name = st.session_state.get("first_name", "Unknown")
customer_last_name = st.session_state.get("last_name", "Unknown")
ai_recommendation = st.session_state.get("ai_response_text", "No recommendation available.")
suggested = st.session_state.get("suggested", "Unknown")
selected_customer_id = st.session_state.get("customer_id", None)
requested_loan_amount = st.session_state.get("requested_loan_amount", "Unknown")

# 🔹 Display Recommendation Details
st.subheader(f"Loan Recommendation for {customer_first_name} {customer_last_name}")
st.text(f"Suggested: {suggested}")
if requested_loan_amount != "Unknown":
    requested_loan_amount = f"${float(requested_loan_amount):,.2f}"
st.text(f"Requested Amount: {requested_loan_amount}")
st.text("\nDetailed AI Analysis:")
st.text(ai_recommendation)

# 🔹 Parse Recommended Loans from AI Response
recommended_loans = []
loan_details = {}
recommendations_section_started = False

for line in ai_recommendation.split("\n"):
    line = line.strip()
    if not line:
        continue

    # Detect when the recommendations section starts
    if "Risk Management & Adjusted Terms:" in line:
        recommendations_section_started = True
        break
    
    # Only add the top 3 loans (starting with 1., 2., 3.) to the recommended_loans list
    if line.startswith(("1.", "2.", "3.")) and not recommendations_section_started:
        recommended_loans.append(line)
        continue

    # Collect detailed loan information for the selected loan
    if line.startswith("   - ") and recommended_loans:
        key_value = line[5:].split(": ", 1)
        if len(key_value) == 2:
            key, value = key_value
            loan_id = recommended_loans[-1].split(" ")[2]
            if loan_id not in loan_details:
                loan_details[loan_id] = {}
            loan_details[loan_id][key] = value

# 🔹 Display only the top 3 loan options for selection
selected_loan_id = None
selected_loan_details = ""

if suggested == "APPROVED":
    st.subheader("Select Final Approved Loan Option")
    if not recommended_loans:
        st.warning("No loan options available to select.")
    else:
        selected_loan = st.radio(
            "Choose the loan to approve:",
            options=recommended_loans[:3],  # Ensure only top 3 are shown
            key="selected_loan"
        )
        
        # Extract the Loan ID from the selected option
        if selected_loan:
            selected_loan_id = selected_loan.split(" ")[2] if len(selected_loan.split(" ")) > 2 else None
            selected_loan_details = selected_loan

# 🔹 Manual Loan Status Update
st.subheader("Manually Edit Loan Status")
manual_loan_status = st.selectbox(
    "Set Loan Status:",
    options=["Approved", "Denied"],
    index=0 if suggested == "APPROVED" else 1,
    key="manual_loan_status"
)

# 🔹 Save Final Approval to Customer Profile
def get_db_connection():
    try:
        DB_USER = os.getenv("USERNAME")
        DB_PASSWORD = os.getenv("DBPASSWORD")
        DB_DSN = os.getenv("DBCONNECTION")
        return oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

if st.button("💾 Save Final Approval & Loan Status"):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()

        #Json patch to update both final_decision and loan_status
        update_data= {
            "final_decision": selected_loan_details if selected_loan_details else "No specific loan selected",
            "loan_status": manual_loan_status
        }
        cursor.execute(
            """
            UPDATE clients_dv 
            SET data = json_mergepatch(data, :1)
            WHERE json_value(data, '$._id') = :2
            """,
            (
                json.dumps(update_data),
                selected_customer_id,
            )
        )
        conn.commit()
        st.success(f"✅ Loan status updated to '{manual_loan_status}' and saved to customer profile!")
        cursor.close()
        conn.close()

# 🔹 Generate PDF with Final Decision
if st.button("📄 Download Recommendation as PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Loan Decision Notice", ln=True, align="C")
    pdf.ln(10)
    
    if manual_loan_status == "Approved" and selected_loan_details:
        # 🎉 Congratulatory Message for Approval
        pdf.cell(200, 10, txt=f"Congratulations {customer_first_name} {customer_last_name}!", ln=True, align="L")
        pdf.cell(200, 10, txt="You have been approved for the following loan:", ln=True, align="L")
        pdf.ln(10)
        
        # Display the approved loan details in the PDF
        pdf.multi_cell(200, 10, txt=f"Loan Details: {selected_loan_details}", align="L")
    
        # If loan details are available, show them
        loan_id = selected_loan_details.split(" ")[2] if len(selected_loan_details.split(" ")) > 2 else "Unknown"
        if loan_id in loan_details and loan_details[loan_id]:
            for key, value in loan_details[loan_id].items():
                pdf.multi_cellcell(0, 10, txt=f"{key}: {value}", align="L")

        pdf.ln(10)
    else:
        pdf.cell(200, 10, txt=f"Hello {customer_first_name} {customer_last_name},", ln=True, align="L")
        pdf.cell(200, 10, txt=f"Unfortunately, you have been denied for your requested loan amount of {requested_loan_amount}.", ln=True, align="L")
        pdf.ln(10)
        
        denial_recommendations = ai_recommendation.split("SUGGESTED: DENIED")[-1].strip()
        if denial_recommendations:
            personalized_recommendations = denial_recommendations.replace(
                "the applicant", f"{customer_first_name} {customer_last_name}"
            )
            pdf.multi_cell(0, 10, txt=personalized_recommendations)
        else:
            pdf.cell(200, 10, txt="We recommend improving your financial profile to increase approval odds.", ln=True, align="L")

    pdf.ln(10)
    pdf.cell(200, 10, txt="For any questions, please contact our support team.", ln=True, align="L")

    pdf_data = pdf.output(dest='S').encode('latin1')

    st.download_button(
        label="📥 Download PDF",
        data=pdf_data,
        file_name=f"Loan_Decision_{customer_first_name}_{customer_last_name}.pdf",
        mime="application/pdf"
    )

# 🔙 Back to Customer Details
if st.button("🔙 Back to Customer Details"):
    st.session_state["current_page"] = "3-customers"
    st.session_state["button_clicked"] = False
    st.session_state["recommendations_generated"] = False
    st.experimental_set_query_params(customer_id=st.session_state["customer_id"])
    st.rerun()
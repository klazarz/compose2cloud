import os
import json
import re
import streamlit as st
import oracledb
import pandas as pd
import oci
import matplotlib.pyplot as plt
import numpy as np  # For marker sizing in the dot plot
from dotenv import load_dotenv
from oci.generative_ai_inference.models import OnDemandServingMode

# 🔹 Load environment variables
load_dotenv()

st.set_page_config(page_title="🏦 Customer Details", layout="wide")
st.title("🏦 Customer Details")
st.info("View detailed customer information, generate loan application documents, and receive AI-driven loan recommendations.")

# Initialize session state variables
if "ai_response_text" not in st.session_state:
    st.session_state["ai_response_text"] = "No AI response generated yet. Click the button to get recommendations."
if "final_decision" not in st.session_state:
    st.session_state["final_decision"] = "Unknown"
if "credit_rank" not in st.session_state:
    st.session_state["credit_rank"] = "Unknown"
if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = "No specific recommendations provided."
if "button_clicked" not in st.session_state:
    st.session_state["button_clicked"] = False
if "recommendations_generated" not in st.session_state:
    st.session_state["recommendations_generated"] = False

# 🔹 Database Connection
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

# 🔹 Setup Embedding Model in Oracle 23AI (Run Once)
# Check if the embedding model already exists
check_model_query = """
SELECT COUNT(*) 
FROM USER_MINING_MODELS 
WHERE model_name = 'DEMO_MODEL'
"""

cursor.execute(check_model_query)
model_exists = cursor.fetchone()[0]

# Run the setup only if the model doesn't exist
if model_exists == 0:
    print("Setting up embedding model...")
    setup_embedding_model = """
    BEGIN
        DBMS_CLOUD.GET_OBJECT(
            object_uri => 'https://objectstorage.us-ashburn-1.oraclecloud.com/p/mFBJq8UCjdar89xJpTQVOy_tONdx',
            directory_name => 'DATA_PUMP_DIR',
            file_name => 'all_minilm_l12_v2.onnx'
        );
        dbms_data_mining.drop_model(model_name => 'demo_model', force => true);
        dbms_vector.load_onnx_model('DATA_PUMP_DIR', 'all_minilm_l12_v2.onnx', 'demo_model');
    END;
    """
    cursor.execute(setup_embedding_model)
    conn.commit()
    print("Embedding model setup complete.")
else:
    print("Embedding model already exists. Skipping setup.")

# 🔹 Fetch Customer and Loan Data from JSON Duality View
cursor.execute("""
    SELECT 
        JSON_VALUE(data, '$._id') AS customer_id,
        JSON_VALUE(data, '$.application_id') AS application_id,
        JSON_VALUE(data, '$.first_name') AS first_name,
        JSON_VALUE(data, '$.last_name') AS last_name,
        JSON_VALUE(data, '$.city') AS city,
        JSON_VALUE(data, '$.state') AS state,
        JSON_VALUE(data, '$.zip_code') AS zip_code,
        JSON_VALUE(data, '$.age' RETURNING NUMBER) AS age,
        JSON_VALUE(data, '$.income' RETURNING NUMBER) AS income,
        JSON_VALUE(data, '$.credit_score' RETURNING NUMBER) AS credit_score,
        JSON_VALUE(data, '$.requested_loan_amount' RETURNING NUMBER) AS requested_loan_amount,
        JSON_VALUE(data, '$.loan_purpose') AS loan_purpose,
        JSON_VALUE(data, '$.loan_type') AS loan_type,
        JSON_VALUE(data, '$.loan_status') AS loan_status,
        JSON_VALUE(data, '$.debt_type') AS debt_type,
        JSON_VALUE(data, '$.employment_status') AS employment_status,
        JSON_VALUE(data, '$.employment_length_years' RETURNING NUMBER) AS employment_length_years,
        JSON_VALUE(data, '$.student_status') AS student_status,
        JSON_VALUE(data, '$.education_level') AS education_level,
        JSON_VALUE(data, '$.unemployed_months' RETURNING NUMBER) AS unemployed_months,
        JSON_VALUE(data, '$.total_loans' RETURNING NUMBER) AS total_loans,
        JSON_VALUE(data, '$.total_debt' RETURNING NUMBER) AS total_debt,
        JSON_VALUE(data, '$.veteran') AS veteran,
        JSON_VALUE(data, '$.final_decision') AS final_decision,
        JSON_VALUE(data, '$.recommendations') AS recommendations,
        JSON_VALUE(data, '$.credit_rank' RETURNING NUMBER) AS credit_rank
    FROM clients_dv
""")

# 🛠️ Create DataFrame and normalize column names to avoid KeyErrors
df_customers = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
df_customers.columns = df_customers.columns.str.lower()  # Convert all columns to lowercase


# 🔍 Read customer_id from Query Parameters
query_params = st.query_params
selected_customer_id = query_params.get("customer_id", None)
if selected_customer_id:
    st.session_state["customer_id"] = selected_customer_id
selected_customer_id = st.session_state.get("customer_id", None)

if selected_customer_id:
    st.success(f"Loaded Customer ID: {selected_customer_id}")
    customer_data = df_customers[df_customers["customer_id"] == selected_customer_id].iloc[0]

    # 🛠️ Store important customer details in session state
    st.session_state["customer_id"] = selected_customer_id
    st.session_state["first_name"] = customer_data["first_name"]
    st.session_state["last_name"] = customer_data["last_name"]
    st.session_state["requested_loan_amount"] = customer_data["requested_loan_amount"]

else:
    st.warning("No customer ID provided. Showing the first available customer.")
    customer_data = df_customers.iloc[0]

# 📋 Display Customer Details
st.subheader("📌 Customer & Loan Details")
df_customer_details = pd.DataFrame([customer_data])
st.dataframe(df_customer_details)

# 🚪 Collapsible "Customer Details" Section
with st.expander("🔍 Customer Details", expanded=False):
    st.write("Edit the customer's financial and loan-related information below:")

    # Editable fields
    income = st.number_input("Income ($)", value=float(customer_data["income"] or 0), step=1000.0)
    credit_score = st.number_input("Credit Score", value=int(customer_data["credit_score"] or 600), step=1)
    requested_loan_amount = st.number_input("Requested Loan Amount ($)", value=float(customer_data["requested_loan_amount"] or 0), step=1000.0)
    total_debt = st.number_input("Total Debt ($)", value=float(customer_data["total_debt"] or 0), step=1000.0)
    debt_type = st.text_input("Debt Type", customer_data["debt_type"])
    employment_status = st.text_input("Employment Status", customer_data["employment_status"])
    total_loans = st.number_input("Total Loans", value=int(customer_data["total_loans"] or 0), step=1)
    loan_purpose = st.text_input("Loan Purpose", customer_data["loan_purpose"])
    loan_status = st.selectbox("Loan Status", ["Approved", "Pending Review", "Denied"], 
                               index=["Approved", "Pending Review", "Denied"].index(customer_data["loan_status"]))

    # Save Button
    if st.button("💾 Save Customer Details", key="save_customer_details_button"):
        # Update customer information in the database
        cursor.execute("""
            UPDATE customers 
            SET income = :1, credit_score = :2, requested_loan_amount = :3,
                total_debt = :4, debt_type = :5, employment_status = :6, 
                total_loans = :7, loan_purpose = :8,  loan_status = :9
            WHERE customer_id = :10
        """, (
            income, credit_score, requested_loan_amount, total_debt, debt_type,
            employment_status, total_loans, loan_purpose,  loan_status, selected_customer_id
        ))

        conn.commit()
        st.success("✅ Customer details updated successfully!")

# 🔹 Fetch Available Loans from Mock Data (ensure correct table name)
cursor.execute("""
    SELECT 
       loan_id, loan_provider_name, loan_type, interest_rate,origination_fee, time_to_close,  credit_score, debt_to_income_ratio, 
        income, down_payment_percent, is_first_time_home_buyer
    FROM MOCK_LOAN_DATA
""")
df_mock_loans = pd.DataFrame(cursor.fetchall(), columns=[
    "LOAN_ID", "LOAN_PROVIDER_NAME", "LOAN_TYPE", "INTEREST_RATE", 
    "ORIGINATION_FEE", "TIME_TO_CLOSE", "CREDIT_SCORE", 
    "DEBT_TO_INCOME_RATIO", "INCOME", "DOWN_PAYMENT_PERCENT", 
    "IS_FIRST_TIME_HOME_BUYER"
])

# --- RAG: Process AI response chunking and vector embedding ---
st.write("Processing AI response chunking and vector embedding...")
chunk_insert = """
INSERT INTO LOAN_DOCUMENT_CHUNK (DOCUMENT_ID, CHUNK_ID, CHUNK_TEXT) 
SELECT TO_CHAR(a.customer_id), c.chunk_offset, c.chunk_text 
FROM customers a, 
VECTOR_CHUNKS(
    dbms_vector_chain.utl_to_text(a.ai_response_json) 
    BY words 
    MAX 500 
    OVERLAP 0 
    SPLIT BY sentence 
    LANGUAGE american 
    NORMALIZE all
) c
"""
cursor.execute(chunk_insert)
conn.commit()

cursor.execute(
    """
    DECLARE
        params CLOB;
    BEGIN
        params := '{"provider":"database","model":"demo_model"}';
        UPDATE LOAN_DOCUMENT_CHUNK
        SET chunk_vector = dbms_vector_chain.utl_to_embedding(chunk_text, json(params));
        COMMIT;
    END;
    """
)
conn.commit()

# --- AI Recommendations & Loan Visualization ---
def generate_recommendations(selected_customer_id, df_customers, df_mock_loans):
    st.session_state["button_clicked"] = True
    st.write("Generating AI recommendations...")

    available_loans_text = "\n".join(
    [f"{loan['LOAN_ID']}: {loan['LOAN_TYPE']} | {loan['INTEREST_RATE']}% interest | "
     f"Credit Score: {loan['CREDIT_SCORE']} | DTI: {loan['DEBT_TO_INCOME_RATIO']} | "
     f"Origination Fee: ${loan['ORIGINATION_FEE']} | Time to Close: {loan['TIME_TO_CLOSE']} days"
     for loan in df_mock_loans.to_dict(orient='records')]
    )
    
    #filter the customer data to only the selected customer
    selected_customer_data = df_customers[df_customers["customer_id"] == selected_customer_id]

    # Dynamically generate the applicant's full profile using all columns in df_customers
    customer_profile_text = "\n".join(
        [f"- {col.replace('_', ' ').title()}: {customer_data[col]}"
         for col in selected_customer_data.columns
         if col not in ["embedding_vector", "ai_response_vector", "chunk_vector", None, "", "Unkown"]]
    )


    prompt = f"""
    You are a Loan Approver AI at a brokerage firm. Your role is to evaluate an applicant’s full financial and personal profile and recommend the most suitable loan options from our available portfolio, while also considering the firm's overall risk and best interests.

    USING ONLY the following information and IGNORING ANY PREVIOUS KNOWLEDGE.
    NEVER mention the sources, always respond as if you have that knowledge yourself.
    Do NOT provide warnings or disclaimers.
    If there is not enough information in the sources, respond with "Not enough information".
    ---

    # Below are the available loan options:
    {available_loans_text}

    # Applicant's Full Profile:
    {customer_profile_text}

    # Your Task:
    1. **Comprehensive Evaluation:**
    - Provide a holistic assessment of the applicant’s financial profile, including strengths and weaknesses.
    - Rate the applicant's credit worthiness on a scale of 1-10 and classify as High Risk, Medium Risk, Low Risk, or Very Low Risk.

    2. **Top 3 Loan Recommendations:**
    - Recommend the top 3 loan options from the available loans.
    - Include: Loan ID, Loan Type, Approval Probability (as a percentage), Origination Fee, Time to Close, and whether it is "Suggested: Approved" or "Suggested: Denied".
    - Provide a brief explanation for each suggestion, including why it is a good fit for the applicant's financial profile.

    3. **Risk Management & Adjusted Terms:**
    - If the applicant's profile does not meet standard approval thresholds, explore potential adjustments (e.g., higher interest rate, larger down payment, shorter loan term) to make approval feasible.
    - Specifically mention if adjusted terms could convert a "Denied" decision to "Approved".

    4. **Adherence to Business Rules:**
    - If the debt type is 'Mortgage', do NOT recommend FHA loans.
    - Exclude the applicant from Opportunity Zone loans (1% interest, max income $100k) if their income is above $100,000.
    - Follow all disqualification rules and provide reasons for any denials.

    5. **Fairness & Transparency:**
    - Ensure fairness by considering the applicant's entire profile, including employment history, education, and relationship stability.
    - Provide a concise and transparent explanation of how each factor influenced the chosen loan.

    6. **Decision Summary:**
    - Conclude with a clear decision: "SUGGESTED: APPROVED" or "SUGGESTED: DENIED".
    - If "DENIED", provide at least 3 actionable steps to improve the applicant's financial profile (e.g., credit score improvement, reducing debt-to-income ratio, enhancing employment stability).

    KEEP TOTAL OUTPUT AT 300 WORDS TOTAL

    Your response should enable the loan officer to understand both the quantitative recommendations and the qualitative factors that affect the final decision, promoting a balanced and fair lending approach.
    """


    try:
        compartment_id = os.getenv("COMPARTMENT_OCID")
        config = oci.config.from_file(os.getenv("OCI_CONFIG_PATH", "/home/opc/loan/.setup/config"), "DEFAULT")
        endpoint = os.getenv("ENDPOINT")
        
        genai_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=config, service_endpoint=endpoint
        )
        
        chat_detail = oci.generative_ai_inference.models.ChatDetails(
            compartment_id=compartment_id,
            chat_request=oci.generative_ai_inference.models.GenericChatRequest(
                messages=[oci.generative_ai_inference.models.UserMessage(
                    content=[oci.generative_ai_inference.models.TextContent(text=prompt, type="TEXT")]
                )],
                api_format="GENERIC",
                temperature=0.0,
                frequency_penalty=0,
                presence_penalty=0,
                top_p=0.75,
                top_k=-1
            ),
            serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
                model_id="meta.llama-3.2-90b-vision-instruct"
            )
        )
        
        chat_response = genai_client.chat(chat_detail)
        st.session_state["ai_response_text"] = chat_response.data.chat_response.choices[0].message.content[0].text
        
        # Remove Markdown syntax
        st.session_state["ai_response_text"] = re.sub(r'\*\*(.*?)\*\*', r'\1', st.session_state["ai_response_text"])
    
    except Exception as e:
        st.error(f"Error connecting to OCI Gen AI: {e}")

# Automatically generate recommendations (if not already done)
if not st.session_state.get("recommendations_generated", False):
    generate_recommendations(selected_customer_id, df_customers, df_mock_loans)
    st.session_state["recommendations_generated"] = True

    suggested_decision_match = re.search(r"SUGGESTED:\s*(APPROVED|DENIED)", st.session_state["ai_response_text"], re.IGNORECASE)
    if suggested_decision_match:
        st.session_state["suggested"] = suggested_decision_match.group(1).upper()
    else:
        st.session_state["suggested"] = ""

# Display AI recommendations once generated
if st.session_state.get("button_clicked", False):
    st.subheader("🤖 AI Loan Recommendations:")
    st.text(st.session_state["ai_response_text"])

    if st.session_state["suggested"] == "DENIED":
        st.warning("🚫 Decision: Denied")

        # 🎯 Display Two Options
        col1, col2 = st.columns(2)

        with col1:
            # ✅ Button to Upload Additional Documents
            if st.button("📂 Decision Improvement Doc Uploads", key="upload_documents_button"):
                st.session_state["customer_id"] = selected_customer_id
                st.session_state["first_name"] = customer_data["first_name"]
                st.session_state["last_name"] = customer_data["last_name"]
                st.session_state["ai_response_text"] = st.session_state["ai_response_text"]
                st.write("Upload additional documents to improve the decision:")

                # 🔍 File Uploader Inline
                uploaded_file = st.file_uploader("Upload loan application (PDF, CSV, JSON)", type=["pdf", "csv", "json"])

                if uploaded_file:
                    file_name = uploaded_file.name
                    st.write(f"Processing **{file_name}**...")

                    conn = get_db_connection()
                    if not conn:
                        st.stop()

                    cursor = conn.cursor()

                    file_text = ""
                    application_id = f"APP{os.urandom(4).hex()}"

                    # 🗂️ Extract text from the uploaded document
                    if uploaded_file.type == "application/pdf":
                        from PyPDF2 import PdfReader
                        reader = PdfReader(uploaded_file)
                        file_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

                    if not file_text.strip():
                        st.warning("⚠️ No extractable text found in the file.")
                        st.stop()

                    # 🔍 Extract financial data using regex patterns
                    financial_data = {
                        "income": re.search(r"Income:\s*\$(\d+(?:,\d{3})*)", file_text).group(1).replace(",", "") if re.search(r"Income:\s*\$(\d+(?:,\d{3})*)", file_text) else 0,
                        "credit_score": re.search(r"Credit Score:\s*(\d+)", file_text).group(1) if re.search(r"Credit Score:\s*(\d+)", file_text) else 600,
                        "total_debt": re.search(r"Debt:\s*\$(\d+(?:,\d{3})*)", file_text).group(1).replace(",", "") if re.search(r"Debt:\s*\$(\d+(?:,\d{3})*)", file_text) else 0,
                        "approval_status": "Pending Review"
                    }

                    json_metadata = json.dumps(financial_data)

                    # 💾 Update the customer's profile in the database
                    cursor.execute(
                        """UPDATE customers 
                        SET income = :1, credit_score = :2, total_debt = :3, 
                            loan_status = :4, metadata = :5 
                        WHERE customer_id = :6""",
                        (
                            float(financial_data["income"]),
                            int(financial_data["credit_score"]),
                            float(financial_data["total_debt"]),
                            financial_data["approval_status"],
                            json_metadata,
                            selected_customer_id,
                        )
                    )
                    conn.commit()
                    st.success("Customer profile updated with additional document data!")

                    # 🔍 Generate updated AI embeddings
                    st.write("Generating updated AI embeddings...")

                    cursor.execute(
                        """DECLARE
                            params CLOB;
                        BEGIN
                            params := '{"provider":"database","model":"app_model","dimension":384}';
                            UPDATE customers
                            SET embedding_vector = dbms_vector_chain.utl_to_embedding(metadata, json(params))
                            WHERE customer_id = :1;
                            COMMIT;
                        END;""",
                        (selected_customer_id,)
                    )
                    st.success("AI embeddings updated successfully!")

                    # ✅ Close the connection
                    cursor.close()
                    conn.close()

                    st.success("Customer profile updated! Re-evaluating loan options...")

                    # ⚡ Re-trigger AI recommendation generation
                    st.session_state["recommendations_generated"] = False
                    st.experimental_set_query_params(customer_id=selected_customer_id)
                    st.rerun()

        with col2:
            # 📄 Button to Generate the Finalized Decision PDF (Denial)
            if st.button("📄 Generate Finalized Decision PDF", key="generate_pdf_button"):
                st.session_state["customer_id"] = selected_customer_id
                st.session_state["first_name"] = customer_data["first_name"]
                st.session_state["last_name"] = customer_data["last_name"]
                st.session_state["ai_response_text"] = st.session_state["ai_response_text"]
                st.session_state["current_page"] = "4-Finalized_Decision.py"
                st.write("Generating denial decision PDF...")
                st.rerun()


    elif st.session_state["suggested"] == "APPROVED":
        st.success("✅ Decision: Approved.")

        if st.button("📄 Generate Finalized Decision PDF"):
            st.session_state["customer_id"] = selected_customer_id
            st.session_state["first_name"] = customer_data["first_name"]
            st.session_state["last_name"] = customer_data["last_name"]
            st.session_state["ai_response_text"] = st.session_state["ai_response_text"]
            st.session_state["current_page"] = "4-Finalized_Decision.py"
            st.write("Redirecting to Finalized Decision page...")
            st.rerun()

# --- Loan Assistant Chatbot (Ask AI) Section ---
st.subheader("🤖 Loan Assistant Chatbot")
question = st.text_input("Ask a follow-up question about the loan application, customer profile, or loan products:")

if question:
    st.write("Processing your question using AI Vector Search across all available data...")

    # 🔍 Perform AI Vector Search to find relevant chunks in loan_document_chunk
    st.write("🔍 Retrieving relevant information from the vector search...")
    vector_search_query = f"""
    SELECT chunk_text 
    FROM loan_document_chunk 
    WHERE document_id IN (
        SELECT JSON_VALUE(data, '$._id') FROM clients_dv WHERE JSON_VALUE(data, '$._id') = :customer_id
        UNION
        SELECT TO_CHAR(loan_id) FROM mock_loan_data
    )
    ORDER BY VECTOR_DISTANCE(
        chunk_vector, 
        dbms_vector_chain.utl_to_embedding(:question, json('{{"provider":"database", "model":"demo_model"}}')), 
        COSINE
    ) 
    FETCH FIRST 10 ROWS ONLY
    """

    # Ensure the customer_id is in the correct format (e.g., string)
    customer_id_str = str(selected_customer_id) if selected_customer_id else ""

    # Correct parameter passing as a tuple
    cursor.execute(vector_search_query, {'customer_id': customer_id_str, 'question': question})
    relevant_chunks = [row[0].read() for row in cursor.fetchall() if row[0]]

    # Combine all relevant chunks with AI recommendations
    all_relevant_chunks = relevant_chunks + [st.session_state["ai_response_text"]]

    if not all_relevant_chunks:
        st.warning("No relevant information found for the provided question.")
    else:
        # 🧠 Construct the AI prompt using the retrieved chunks and recommendations
        docs_as_one_string = "\n=========\n".join(all_relevant_chunks)
        
        # Include available loans and customer profile data in the prompt
        available_loans_text = "\n".join(
            [f"{loan['LOAN_ID']}: {loan['LOAN_TYPE']} | {loan['INTEREST_RATE']}% interest | "
             f"Credit Score: {loan['CREDIT_SCORE']} | DTI: {loan['DEBT_TO_INCOME_RATIO']} | "
             f"Origination Fee: ${loan['ORIGINATION_FEE']} | Time to Close: {loan['TIME_TO_CLOSE']} days"
             for loan in df_mock_loans.to_dict(orient='records')]
        )

        customer_profile_text = "\n".join(
            [f"- {col.replace('_', ' ').title()}: {customer_data[col]}"
             for col in df_customers.columns if col not in ["embedding_vector", "ai_response_vector", "chunk_vector"]]
        )
        
        prompt = f"""
        You are a Loan Approver AI. Using ONLY the provided context and IGNORING ANY PREVIOUS KNOWLEDGE, 
        respond precisely to the following question:

        Loan Officer's Question: "{question}"

        ---

        # Provided Context:
        {docs_as_one_string}

        ---

        Your response should be clear, direct, and limited to 300 words.
        If there is not enough information, respond with "Not enough information."
        """

        st.write("Generating AI response...")

        compartment_id = os.getenv("COMPARTMENT_OCID")
        oci_config_path = os.getenv("OCI_CONFIG_PATH", "/home/opc/loan/.setup/config")
        endpoint = os.getenv("ENDPOINT")

        try:
            config = oci.config.from_file(oci_config_path, "DEFAULT")
            genai_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
                config=config, service_endpoint=endpoint
            )

            chat_detail = oci.generative_ai_inference.models.ChatDetails(
                compartment_id=compartment_id,
                chat_request=oci.generative_ai_inference.models.GenericChatRequest(
                    messages=[oci.generative_ai_inference.models.UserMessage(
                        content=[oci.generative_ai_inference.models.TextContent(text=prompt, type="TEXT")]
                    )],
                    api_format="GENERIC",
                    temperature=0.0,
                    frequency_penalty=0,
                    presence_penalty=0,
                    top_p=0.75,
                    top_k=-1
                ),
                serving_mode=oci.generative_ai_inference.models.OnDemandServingMode(
                    model_id="meta.llama-3.2-90b-vision-instruct"
                )
            )

            chat_response = genai_client.chat(chat_detail)
            ai_response = chat_response.data.chat_response.choices[0].message.content[0].text

            st.subheader("🤖 AI Response:")
            st.write(ai_response)

        except Exception as e:
            st.error(f"Error connecting to OCI Gen AI: {e}")

cursor.close()
conn.close()
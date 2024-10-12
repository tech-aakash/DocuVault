import streamlit as st
from helper import forgot_password, confirm_forgot_password, get_user_id_from_email
from neo4j import GraphDatabase

from dotenv import load_dotenv
import os

load_dotenv('api.env')

# Now you can use the environment variables, for example:
NEO4J_LINK = os.getenv('NEO4J_LINK')
NEO4J_API_KEY = os.getenv('NEO4J_API_KEY')
COGNITO_CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
BREVO_API_KEY = os.getenv('BREVO_API_KEY')
# Initialize Neo4j driver
driver = GraphDatabase.driver(NEO4J_LINK, auth=("neo4j", NEO4J_API_KEY))

def app():
    # Clear other session states that are not relevant for login
    st.session_state.pop('details_saved', None)
    st.session_state.pop('uploaded_file_path', None)
    st.session_state.pop('extracted_details', None)
    st.session_state.pop('document_type', None)

    st.header("Login")

    user_id_input = st.text_input("Enter your user ID for login:")
    email_login_input = st.text_input("Enter your email address for login:", key='login_email')

    if st.button("Send OTP for Login"):
        if user_id_input and email_login_input:
            # Verify if user_id and email match in Neo4j
            with driver.session() as session:
                result = session.run("MATCH (u:User {user_id: $user_id, email: $email}) RETURN u", user_id=user_id_input, email=email_login_input)
                if result.single():
                    forgot_password(email_login_input)
                    st.success("OTP sent to your email address.")
                else:
                    st.error("User ID and email do not match.")

    otp_login_input = st.text_input("Enter the OTP sent to your email for login:")

    if st.button("Verify OTP and Login"):
        if otp_login_input and st.session_state.login_email:
            response = confirm_forgot_password(st.session_state.login_email, otp_login_input, 'TemporaryPassword123!')
            if 'error' not in response:
                st.session_state.user_id = user_id_input
                st.session_state.email = st.session_state.login_email
                st.success("Logged in successfully!")
                st.session_state.screen = 'Dashboard'
                st.experimental_rerun()
            else:
                st.error("Invalid OTP. Please try again.")

    if st.button("Back"):
        st.session_state.screen = 'Home'
        st.experimental_rerun()

    st.write(f"Current screen: {st.session_state.get('screen', 'None')}")
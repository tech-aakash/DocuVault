import streamlit as st
from streamlit_lottie import st_lottie
import requests
from helper import get_user_id_from_email, send_user_id_email

# Function to load Lottie animation from URL
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load the Lottie animation
lottie_forgot_user = load_lottie_url("https://lottie.host/5c904eef-6cd0-413f-812b-18b4bbecbc05/uOMHRBoQyI.json")

# CSS for custom styling (using variables from toml theme)
def add_custom_css():
    st.markdown("""
    <style>
    /* Style the input box */
    input[type="text"] {
        padding: 10px !important;
        border-radius: 10px !important;
        border: 1px solid #D1D5DB !important;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1) !important;
        font-size: 16px !important;
        background-color: #1F2937 !important;  /* Dark background */
        color: white !important;  /* White text inside input box */
    }

    /* Style the buttons */
    .stButton button {
        width: 100% !important;  /* Full width buttons */
        height: 50px !important;  /* Set fixed height */
        font-size: 18px !important;
        background-color: #4F46E5 !important;  /* Matches primaryColor */
        color: white !important;
        border-radius: 10px !important;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, background-color 0.2s;
    }

    /* Hover effect for the buttons */
    .stButton button:hover {
        background-color: #3730A3 !important;  /* Darker blue for hover effect */
        transform: scale(1.05);
    }

    /* Header text styling */
    h1 {
        color: #4F46E5 !important;  /* Primary color for header */
        text-align: center !important;
    }

    /* Success and error messages */
    .stAlert div {
        color: white !important;  /* Text color for alerts */
        background-color: #4B5563 !important;  /* Darker background for success/error messages */
        border-radius: 10px !important;
        padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# Call the custom CSS function
add_custom_css()

def app():
    # Display the Lottie animation at the top
    st_lottie(lottie_forgot_user, height=200, key="forgot_user_anim")

    # Styled header for the "Forgot User ID" page
    st.markdown("<h1>Forgot User ID</h1>", unsafe_allow_html=True)

    # Input field with placeholder and styled
    forgot_email_input = st.text_input("Enter your registered email address:")

    # Place the "Send User ID" button directly below the input field
    if st.button("Send User ID"):
        if forgot_email_input:
            user_id = get_user_id_from_email(forgot_email_input)
            if user_id:
                send_user_id_email(forgot_email_input, user_id)
                st.success("Your User ID has been sent to your email address. Please check your inbox/spam.")
            else:
                st.error("This email is not registered. Please check and try again.")
        else:
            st.error("Please enter a valid email address.")

    # Place the "Back" button below the "Send User ID" button with consistent styling
    if st.button("Back"):
        st.session_state.screen = 'Home'
        st.experimental_rerun()

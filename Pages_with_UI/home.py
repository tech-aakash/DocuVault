import streamlit as st
from streamlit_lottie import st_lottie
import requests

# Function to load Lottie animation from URL
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load a single Lottie animation
lottie_create_user = load_lottie_url("https://lottie.host/5fe1751e-52f7-4cfd-9dbe-e75105b3e745/I4ofjUqWYU.json")

def app():
    st.title("User Creation and Login System")

    # Lottie animation at the top
    st_lottie(lottie_create_user, height=300, key="create_user_anim")

    # Center the welcome text
    st.markdown("<h3 style='text-align: center;'>Welcome! Please choose an action below:</h3>", unsafe_allow_html=True)

    # Create three equal-sized columns for buttons
    col1, col2, col3 = st.columns([1, 1, 1], gap="large")  # Equal column sizes

    # Define a CSS style block for uniform button sizes
    button_style = """
    <style>
    .stButton button {
        width: 100% !important;  /* Forces buttons to take full width */
        height: 50px !important;  /* Set fixed height for all buttons */
        font-size: 18px !important;
        background-color: #4F46E5 !important;
        color: white !important;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, background-color 0.2s;
    }
    .stButton button:hover {
        background-color: #3730A3 !important;
        transform: scale(1.05);
    }
    </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)

    # Equal-sized buttons in the columns
    with col1:
        if st.button("Create User"):
            st.session_state.screen = 'Create User'
            st.experimental_rerun()

    with col2:
        if st.button("Login"):
            st.session_state.screen = 'Login'
            st.experimental_rerun()

    with col3:
        if st.button("Forgot User ID"):
            st.session_state.screen = 'Forgot User ID'
            st.experimental_rerun()

    # Add a divider
    st.markdown('<hr>', unsafe_allow_html=True)

    # Display the current screen
    st.write(f"Current screen: {st.session_state.get('screen', 'None')}")

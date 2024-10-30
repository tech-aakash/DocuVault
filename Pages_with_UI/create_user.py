import streamlit as st
from helper import sign_up_user, confirm_user_sign_up, is_email_registered, generate_user_id, store_user

def app():
    # Center the title
    st.markdown("<h1 style='text-align: center;'>Create Your Account</h1>", unsafe_allow_html=True)

    # CSS to style buttons and input fields uniformly and remove only the space between label and input box
    custom_style = """
    <style>
    .stButton button {
        width: 100% !important;  /* Full width buttons */
        height: 50px !important;  /* Set fixed height */
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

    /* Targeting the container to remove only the margin (without touching padding or dimensions) */
    div[data-baseweb="input"] {
        margin-top: 0px !important;
    }
    </style>
    """
    st.markdown(custom_style, unsafe_allow_html=True)

    # Left-align the custom label for email input, keeping the default spacing of the input box
    st.markdown("<h3 style='text-align: left; font-size: 22px; margin-bottom: 0;'>Enter your email address for account creation:</h3>", unsafe_allow_html=True)

    # Email input for account creation with no label (box dimensions unchanged)
    email_input = st.text_input("", key='create_email')

    # Check if the user has already clicked "Send OTP"
    if 'otp_sent' not in st.session_state:
        st.session_state.otp_sent = False

    # Step 1: Email entry and send OTP button
    if not st.session_state.otp_sent:
        if st.button("Send OTP for Account Creation"):
            if email_input:
                if is_email_registered(email_input):
                    st.error("This email is already registered. Please use a different email.")
                else:
                    sign_up_user(email_input)
                    st.session_state.otp_sent = True  # Mark that OTP is sent
                    st.success("OTP sent to your email address.")
            else:
                st.error("Please enter an email address.")
    
    # Step 2: Show OTP input and verification button if OTP is sent
    if st.session_state.otp_sent:
        otp_input = st.text_input("Enter the OTP sent to your email for account creation:")

        if st.button("Verify OTP and Create Account"):
            if otp_input and st.session_state.create_email:
                response = confirm_user_sign_up(st.session_state.create_email, otp_input)
                if 'error' not in response:
                    user_id = generate_user_id()
                    store_user(user_id, st.session_state.create_email)
                    st.session_state.user_id = user_id
                    st.session_state.email = st.session_state.create_email
                    st.success(f"Account created successfully! Your user ID is: {user_id}")
                    st.session_state.screen = 'Dashboard'
                    st.experimental_rerun()
                else:
                    st.error("Invalid OTP. Please try again.")
            else:
                st.error("Please enter the OTP.")

    # Back button to return to the home screen
    if st.button("Back"):
        st.session_state.screen = 'Home'
        st.experimental_rerun()

    # Display current screen for debugging
    st.write(f"Current screen: {st.session_state.get('screen', 'None')}")
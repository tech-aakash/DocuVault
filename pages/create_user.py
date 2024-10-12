import streamlit as st
from helper import sign_up_user, confirm_user_sign_up, is_email_registered, generate_user_id, store_user

def app():
    st.header("Create User ID")

    email_input = st.text_input("Enter your email address for account creation:", key='create_email')
    
    if st.button("Send OTP for Account Creation"):
        if email_input:
            if is_email_registered(email_input):
                st.error("This email is already registered. Please use a different email.")
            else:
                sign_up_user(email_input)
                st.success("OTP sent to your email address.")

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

    if st.button("Back"):
        st.session_state.screen = 'Home'
        st.experimental_rerun()

    st.write(f"Current screen: {st.session_state.get('screen', 'None')}")

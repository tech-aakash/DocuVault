import streamlit as st
from helper import get_user_id_from_email, send_user_id_email

def app():
    st.header("Forgot User ID")

    forgot_email_input = st.text_input("Enter your registered email address:")
    
    if st.button("Send User ID"):
        if forgot_email_input:
            user_id = get_user_id_from_email(forgot_email_input)
            if user_id:
                send_user_id_email(forgot_email_input, user_id)
                st.success("Your User ID has been sent to your email address. Please check your inbox/spam.")
            else:
                st.error("This email is not registered. Please check and try again.")
    
    if st.button("Back"):
        st.session_state.screen = 'Home'
        st.experimental_rerun()

    st.write(f"Current screen: {st.session_state.get('screen', 'None')}")

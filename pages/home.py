import streamlit as st

def app():
    st.title("User Creation and Login System")

    if st.button("Create User"):
        st.session_state.screen = 'Create User'
        st.experimental_rerun()
    
    if st.button("Login"):
        st.session_state.screen = 'Login'
        st.experimental_rerun()
    
    if st.button("Forgot User ID"):
        st.session_state.screen = 'Forgot User ID'
        st.experimental_rerun()

    st.write(f"Current screen: {st.session_state.get('screen', 'None')}")

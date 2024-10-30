import streamlit as st
from helper import get_issued_documents, decrypt_data, generate_encryption_key
from streamlit_lottie import st_lottie
import requests

# Function to load the Lottie animation from the URL
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def app():
    # Center the header and style it
    st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>Issued Documents</h1>", unsafe_allow_html=True)

    # Load the Lottie animation from the given URL
    lottie_animation = load_lottie_url("https://lottie.host/9694ed71-9486-48c3-8a97-578b7bf63258/841dbJff56.json")

    # Display the Lottie animation below the heading (adjust width and height as needed)
    if lottie_animation:
        st_lottie(lottie_animation, width=300, height=300, key="issued_docs_anim")

    # Custom CSS for styling the selectbox and buttons
    custom_style = """
    <style>
    .stSelectbox select {
        width: 100% !important;
        padding: 10px !important;
        font-size: 16px !important;
        border-radius: 8px !important;
        border: 1px solid #4F46E5 !important;
        color: #374151 !important;
    }
    
    .stButton button {
        width: 100% !important;
        height: 45px !important;
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

    .stMarkdown h1 {
        font-size: 28px;
        color: #4F46E5;
    }
    </style>
    """
    st.markdown(custom_style, unsafe_allow_html=True)
    
    # Retrieve issued documents for the logged-in user
    issued_docs = get_issued_documents(st.session_state.user_id)
    
    if issued_docs:
        # Create a selectbox for choosing a document to view
        selected_doc = st.selectbox("Select a document to view", list(issued_docs.keys()))

        # Style the view button and add functionality
        if st.button(f"View {selected_doc.replace('_', ' ')}"):
            st.session_state.selected_doc = selected_doc
            st.session_state.issued_docs = issued_docs
            st.session_state.screen = 'Decrypt Document'
            st.experimental_rerun()
    else:
        # Display a styled message if no documents are available
        st.markdown("<p style='text-align: center; color: #EF4444;'>No documents have been issued.</p>", unsafe_allow_html=True)
    
    # Style the back button and add functionality
    if st.button("Back"):
        st.session_state.view = 'options'
        st.session_state.screen = 'Dashboard'
        st.experimental_rerun()


import streamlit as st
import json  # Import json module to handle JSON deserialization
from helper import decrypt_data, generate_encryption_key

def app():
    # Custom CSS for styling inputs, buttons, and headers
    custom_style = """
    <style>
    .stTextInput input {
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

    .stMarkdown p {
        color: #374151 !important;
    }

    .stError {
        color: #EF4444 !important;
        font-weight: bold;
    }
    </style>
    """
    st.markdown(custom_style, unsafe_allow_html=True)

    # Center the header and style it
    st.markdown(f"<h1 style='text-align: center; color: #4F46E5;'>Decrypt {st.session_state.selected_doc.replace('_', ' ')}</h1>", unsafe_allow_html=True)
    
    # User input for User ID and Year of Birth
    user_id_input = st.text_input("Enter your User ID")
    year_of_birth_input = st.text_input("Enter your Year of Birth")
    
    # Decrypt button with enhanced UI
    if st.button("Decrypt Document"):
        if user_id_input == st.session_state.user_id and year_of_birth_input.isdigit():
            key = generate_encryption_key(year_of_birth_input, user_id_input)
            
            # Deserialize the JSON string back into a dictionary
            encrypted_details = json.loads(st.session_state.issued_docs[st.session_state.selected_doc])
            
            decrypted_details = {}
            for field, encrypted_data in encrypted_details.items():
                iv = encrypted_data['iv']
                ct = encrypted_data['ct']
                decrypted_details[field] = decrypt_data(iv, ct, key)
            
            st.write("### Decrypted Details:")
            # Display each decrypted field with appropriate styling
            for field, value in decrypted_details.items():
                st.markdown(f"**{field}:** {value}")
        else:
            st.markdown("<p class='stError'>Invalid User ID or Year of Birth.</p>", unsafe_allow_html=True)

    # Back and Logout buttons styled
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Back"):
            st.session_state.screen = 'Issued Documents'
            st.experimental_rerun()

    with col2:
        if st.button("Logout"):
            st.session_state.screen = 'Home'
            st.session_state.user_id = ''
            st.session_state.email = ''
            st.experimental_rerun()

    # Current screen for debugging or info (optional)
    st.write(f"Current screen: {st.session_state.get('screen', 'None')}")

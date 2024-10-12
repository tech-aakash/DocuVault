import streamlit as st
import json  # Import json module to handle JSON deserialization
from helper import decrypt_data, generate_encryption_key

def app():
    st.header(f"Decrypt {st.session_state.selected_doc.replace('_', ' ')}")
    
    user_id_input = st.text_input("Enter your User ID")
    year_of_birth_input = st.text_input("Enter your Year of Birth")
    
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
            
            st.write("Decrypted Details:")
            for field, value in decrypted_details.items():
                st.write(f"{field}: {value}")
        else:
            st.error("Invalid User ID or Year of Birth.")
    
    if st.button("Back"):
        st.session_state.screen = 'Issued Documents'
        st.experimental_rerun()

    if st.button("Logout"):
        st.session_state.screen = 'Home'
        st.session_state.user_id = ''
        st.session_state.email = ''
        st.experimental_rerun()

    st.write(f"Current screen: {st.session_state.get('screen', 'None')}")


import streamlit as st
from helper import store_encrypted_document

def app():
    st.header("Validation of Uploaded Document")
    st.write("Below are the extracted details from the uploaded document. Please verify and make any necessary corrections.")

    if 'details_saved' not in st.session_state:
        st.session_state.details_saved = False

    # Define expected fields for the document
    expected_fields = ['Name', 'Identity Number', 'Date of Birth', 'Year of Birth', 'Authority']

    # Display and allow editing of all fields
    for field in expected_fields:
        if field not in st.session_state.extracted_details:
            st.session_state.extracted_details[field] = ''
        st.session_state.extracted_details[field] = st.text_input(field, st.session_state.extracted_details[field])

    if st.button("Confirm and Save"):
        year_of_birth = st.session_state.extracted_details.get('Year of Birth')
        if year_of_birth:
            store_encrypted_document(st.session_state.user_id, year_of_birth, st.session_state.document_type, st.session_state.extracted_details)
            st.session_state.details_saved = True
        else:
            st.error("Year of birth is missing or invalid.")

    if st.session_state.details_saved:
        st.success("Details have been validated and saved successfully.")

    if st.button("Back"):
        st.session_state.details_saved = False
        st.session_state.screen = 'Dashboard'
        st.experimental_rerun()

    st.write(f"Current screen: {st.session_state.get('screen', 'None')}")

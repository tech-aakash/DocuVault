import os
import streamlit as st
from helper import (
    run_model_on_document, 
    get_issued_documents, 
    check_uploaded_document, 
    check_user_id_exists, 
    send_otp_to_user, 
    confirm_otp, 
    add_family_member_to_db, 
    get_family_members,
    remove_family_member_from_db
)

def app():
    st.header("Dashboard")
    st.write(f"User ID: {st.session_state.user_id}")
    st.write(f"Email: {st.session_state.email}")

    # Initialize view in session state
    if 'view' not in st.session_state:
        st.session_state.view = 'options'

    if st.session_state.view == 'options':
        st.subheader("Options")
        
        if st.button("Add Family Member"):
            st.session_state.view = 'add_family'
            st.experimental_rerun()

        if st.button("View Issued Documents"):
            st.session_state.view = 'issued_documents'
            st.experimental_rerun()

        if st.button("Upload Documents"):
            st.session_state.view = 'upload'
            st.experimental_rerun()

        if st.button("Logout"):
            st.session_state.screen = 'Home'
            st.session_state.user_id = ''
            st.session_state.email = ''
            st.experimental_rerun()

        # Display family members
        family_members = get_family_members(st.session_state.user_id)
        if family_members:
            st.subheader("Family Members:")
            for member in family_members:
                st.write(f"Name: {member['family_name']}, Email: {member['family_email']}")
                if st.button(f"Remove {member['family_name']}"):
                    remove_family_member_from_db(st.session_state.user_id, member['family_user_id'])
                    st.success(f"{member['family_name']} removed successfully!")
                    st.experimental_rerun()

    elif st.session_state.view == 'add_family':
        st.subheader("Add New Family Member")

        family_user_id = st.text_input("Enter Family Member's User ID")

        if st.button("Search User ID"):
            if check_user_id_exists(family_user_id):
                st.success("User found! Sending OTP...")
                st.session_state.family_user_id = family_user_id  # Store family user ID in session
                otp_sent = send_otp_to_user(family_user_id)
                if otp_sent:
                    st.success("OTP sent to family member!")
                else:
                    st.error("Failed to send OTP. You can still proceed with adding the family member.")
            else:
                st.error("User not found.")
        
        if "family_user_id" in st.session_state:
            # Show the relationship selection immediately after the user is found
            relationship = st.selectbox("Select relationship", ["Spouse", "Child", "Parent", "Sibling"])

            otp_input = st.text_input("Enter OTP sent to family member")

            if st.button("Confirm OTP"):
                if confirm_otp(st.session_state.family_user_id, otp_input):
                    # Add family member only after OTP is confirmed and relationship is selected
                    add_family_member_to_db(st.session_state.user_id, st.session_state.family_user_id, relationship)
                    st.success(f"Family member added as {relationship} successfully!")
                    
                    # Clear family_user_id from session state
                    del st.session_state.family_user_id
                    
                    # Automatically switch back to the main dashboard view
                    st.session_state.view = 'options'
                    st.experimental_rerun()
                else:
                    st.error("Invalid OTP. Please try again.")


    elif st.session_state.view == 'issued_documents':
        st.subheader("Issued Documents")
        issued_docs = get_issued_documents(st.session_state.user_id)
        for doc_type, details in issued_docs.items():
            st.write(f"{doc_type}: {details}")
        if st.button("Back"):
            st.session_state.view = 'options'
            st.experimental_rerun()

    elif st.session_state.view == 'upload':
        st.subheader("Upload Documents")
        document_types = ["Aadhar Card", "Voter ID", "Pan Card", "Passport"]
        available_doc_types = [doc for doc in document_types if not check_uploaded_document(st.session_state.user_id, doc)]

        if available_doc_types:
            doc_type = st.selectbox("Select Document Type", available_doc_types)
            uploaded_file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png", "pdf"])

            if uploaded_file is not None:
                file_path = os.path.join("uploads", st.session_state.user_id, doc_type)
                os.makedirs(file_path, exist_ok=True)
                file_full_path = os.path.join(file_path, uploaded_file.name)

                if st.button("Upload"):
                    with open(file_full_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.session_state.uploaded_file_path = file_full_path
                    st.success(f"{doc_type} uploaded successfully!")
                    st.session_state.extracted_details = run_model_on_document(file_full_path, doc_type)
                    st.session_state.document_type = doc_type
                    st.session_state.screen = 'Validation'
                    st.experimental_rerun()
        else:
            st.write("All document types have been uploaded.")

        if st.button("Back"):
            st.session_state.view = 'options'
            st.experimental_rerun()

    st.write(f"Current screen: {st.session_state.get('screen', 'None')}")

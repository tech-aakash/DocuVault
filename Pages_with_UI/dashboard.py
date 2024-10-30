import os
import streamlit as st
from streamlit_lottie import st_lottie
import requests
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

# Function to load Lottie animation from URL
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def app():
    st.markdown("<h1 style='text-align: center; color: #FFFFFF;'>Dashboard</h1>", unsafe_allow_html=True)
    
    # Load Lottie animation
    lottie_animation = load_lottie_url("https://lottie.host/46f183b8-ca00-497a-8537-77d324cd7a4e/89TF1x1Dvx.json")
    
    # Display Lottie animation below dashboard header
    if lottie_animation:
        st_lottie(lottie_animation, height=250, key="dashboard_animation")
    
    st.write(f"**User ID**: {st.session_state.user_id}")
    st.write(f"**Email**: {st.session_state.email}")

    # Initialize view in session state
    if 'view' not in st.session_state:
        st.session_state.view = 'options'

    # CSS to style buttons and input fields
    button_style = """
    <style>
    .stButton button {
        width: 100% !important;  /* Full width buttons */
        height: 50px !important;  /* Fixed height */
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

    if st.session_state.view == 'options':
        st.subheader("Options")

        # Create a grid for the options to appear as buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Add Family Member"):
                st.session_state.view = 'add_family'
                st.experimental_rerun()

            if st.button("View Issued Documents"):
                st.session_state.view = 'issued_documents'
                st.experimental_rerun()

        with col2:
            if st.button("Upload Documents"):
                st.session_state.view = 'upload'
                st.experimental_rerun()

            if st.button("Logout"):
                st.session_state.screen = 'Home'
                st.session_state.user_id = ''
                st.session_state.email = ''
                st.experimental_rerun()

        # Display family members in a styled manner
        family_members = get_family_members(st.session_state.user_id)
        if family_members:
            st.subheader("Family Members:")
            for member in family_members:
                st.write(f"**Name**: {member['family_name']}, **Email**: {member['family_email']}")
                if st.button(f"Remove {member['family_name']}"):
                    remove_family_member_from_db(st.session_state.user_id, member['family_user_id'])
                    st.success(f"{member['family_name']} removed successfully!")
                    st.experimental_rerun()

    elif st.session_state.view == 'add_family':
        st.subheader("Add New Family Member")

        # Text input to enter the family member's user ID
        family_user_id = st.text_input("Enter Family Member's User ID")

        # "Search User ID" button
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
        
        # After user ID is found, show OTP and relationship selection fields
        if "family_user_id" in st.session_state:
            relationship = st.selectbox("Select relationship", ["Spouse", "Child", "Parent", "Sibling"])
            otp_input = st.text_input("Enter OTP sent to family member")

            # "Confirm OTP" button
            if st.button("Confirm OTP"):
                if confirm_otp(st.session_state.family_user_id, otp_input):
                    add_family_member_to_db(st.session_state.user_id, st.session_state.family_user_id, relationship)
                    st.success(f"Family member added as {relationship} successfully!")
                    del st.session_state.family_user_id  # Clear family_user_id from session state
                    st.session_state.view = 'options'  # Go back to the dashboard
                    st.experimental_rerun()
                else:
                    st.error("Invalid OTP. Please try again.")
        
        # "Back" button to return to the main dashboard without adding a family member
        if st.button("Back"):
            st.session_state.view = 'options'  # Return to the options screen
            st.experimental_rerun()

    elif st.session_state.view == 'issued_documents':
        # st.subheader("Issued Documents")
        # issued_docs = get_issued_documents(st.session_state.user_id)
        # for doc_type, details in issued_docs.items():
        #     st.write(f"**{doc_type}**: {details}")
        # if st.button("Back"):
        #     st.session_state.view = 'options'
        st.session_state.screen = 'Issued Documents'
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

import streamlit as st
from helper import get_issued_documents, decrypt_data, generate_encryption_key

def app():
    st.header("Issued Documents")
    
    # Retrieve all issued documents for the logged-in user
    issued_docs = get_issued_documents(st.session_state.user_id)
    print(issued_docs)  # Debugging print to check what documents are retrieved
    
    if issued_docs:
        selected_doc = st.selectbox("Select a document to view", list(issued_docs.keys()))
        
        if st.button(f"View {selected_doc.replace('_', ' ')}"):
            st.session_state.selected_doc = selected_doc
            st.session_state.issued_docs = issued_docs
            st.session_state.screen = 'Decrypt Document'
            st.experimental_rerun()
    else:
        st.write("No documents have been issued.")
    
    if st.button("Back"):
        st.session_state.view = 'options'
        st.session_state.screen = 'Dashboard'
        st.experimental_rerun()

import streamlit as st
from multipage import MultiPage
from pages import home, login, dashboard, validation, create_user, forgot_user_id, issued_documents, decrypt_document

# Initialize session state
if 'button_clicked' not in st.session_state:
    st.session_state.button_clicked = False

app = MultiPage()

# Add all your application here
app.add_page("Home", home.app)
app.add_page("Create User", create_user.app)
app.add_page("Login", login.app)
app.add_page("Forgot User ID", forgot_user_id.app)
app.add_page("Dashboard", dashboard.app)
app.add_page("Validation", validation.app)
app.add_page("Issued Documents", issued_documents.app)
app.add_page("Decrypt Document", decrypt_document.app)

# Run the main app
app.run()

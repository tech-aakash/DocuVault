import streamlit as st

class MultiPage:
    def __init__(self):
        self.pages = []

    def add_page(self, title, func):
        self.pages.append({
            "title": title,
            "function": func
        })

    def run(self):
        # If the session state has a screen value, use it
        if 'screen' in st.session_state:
            selected_page = st.session_state.screen
        else:
            selected_page = 'Home'

        page_titles = [page['title'] for page in self.pages]

        if selected_page not in page_titles:
            selected_page = 'Home'

        # Sidebar navigation
        st.sidebar.title('Navigation')
        selected_page = st.sidebar.radio(
            'Go to',
            self.pages,
            format_func=lambda page: page['title'],
            index=page_titles.index(selected_page)
        )

        # Run the function of the selected page
        selected_page['function']()

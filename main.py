import streamlit as st
from db_user import verify_user

def main():
    st.set_page_config(
        page_title="TextSum App",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Check if user is logged in
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
    
    # If logged in, show the model page
    if st.session_state.logged_in:
        st.switch_page("pages/model.py")
    else:
        st.switch_page("pages/home.py")

if __name__ == "__main__":
    main()
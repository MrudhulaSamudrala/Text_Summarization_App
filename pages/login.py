import streamlit as st
from db_user import verify_user

# Page configuration
st.set_page_config(page_title="Login - TextSum", layout="centered")

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0066ff22, #7c3aed22);
        background-attachment: fixed;
    }
    
    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 4rem;
        margin-top: 4rem;
    }
            
    .stMain{
            padding-top: 3rem;
             margin-top: 3rem;
            }

    .login-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .gradient-text {
        background: linear-gradient(45deg, #0066ff, #e33dbf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        padding-top:3rem;
        margin-top:3rem;
    }
    
    .stTextInput > div > div {
        background-color: white;
        border-radius: 10px;
        border: 1px solid #ddd;
        padding: 0.5rem;
    }
    
    .stTextInput > div > div:focus-within {
        border-color: #7c3aed;
        box-shadow: 0 0 8px rgba(124, 58, 237, 0.3);
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #0066ff, #7c3aed);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(124, 58, 237, 0.3);
    }
    
    .divider {
        margin: 2rem 0;
        border-top: 1px solid #ddd;
    }
    
    .signup-text {
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 1rem;
    }

    /* Hide the empty block */
    header {
        display: none !important;
    }
    
    /* Remove white space and header */
    .block-container {
        padding: 0rem !important;
        margin-top: -2rem !important;
    }
    
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    #MainMenu {
        display: none !important;
    }
    
    [data-testid="stToolbar"] {
        display: none !important;
    }
    
    [data-testid="stDecoration"] {
        display: none !important;
    }
    
    footer {
        display: none !important;
    }
    
     /* Hide password reveal icon */
    button[title="View password"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Login form container
#st.markdown('<div class="login-container">', unsafe_allow_html=True)
st.markdown('<h1 class="gradient-text">Welcome Back</h1>', unsafe_allow_html=True)

username = st.text_input("Username", placeholder="Enter your username")
password = st.text_input("Password", type="password", placeholder="Enter your password")

col1, col2 = st.columns(2)

with col1:
    if st.button("Login", use_container_width=True):
        if username and password:
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.switch_page("pages/model.py")
            else:
                st.error("Invalid username or password")
        else:
            st.warning("Please enter both username and password")

with col2:
    if st.button("Back to Home", use_container_width=True):
        st.switch_page("pages/home.py")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<p class="signup-text">Don\'t have an account?</p>', unsafe_allow_html=True)

if st.button("Sign Up Here", use_container_width=True):
    st.switch_page("pages/signup.py")

st.markdown('</div>', unsafe_allow_html=True)
import streamlit as st
from db_user import create_user

# Page configuration
st.set_page_config(page_title="Sign Up - TextSum",layout="centered")

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0066ff22, #7c3aed22);
        background-attachment: fixed;
    }

    /* Hide Streamlit elements */
    #MainMenu, header, footer, [data-testid="stToolbar"] {
        display: none !important;
    }
    
    .block-container {
        padding-top: 2rem !important;
    }
    
    .signup-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .gradient-text {
        background: linear-gradient(45deg, #0066ff, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .stTextInput > div > div {
        background-color: white;
        border-radius: 10px;
        border: 1px solid #ddd;
        padding: 0.5rem;
    }
    
    .stTextInput > div > div:focus-within {
        border-color: #7c3aed;
        box-shadow: 0 0 8px rgba(124, 58, 237, 0.2);
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
    
    .login-text {
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# st.markdown('<div class="signup-container">', unsafe_allow_html=True)
st.markdown('<h1 class="gradient-text">Create Account</h1>', unsafe_allow_html=True)

username = st.text_input("Username", placeholder="Choose a username")
email = st.text_input("Email", placeholder="Enter your email")
password = st.text_input("Password", type="password", placeholder="Create a password")
confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")

col1, col2 = st.columns(2)

with col1:
    if st.button("Sign Up", use_container_width=True):
        if username and email and password and confirm_password:
            if password != confirm_password:
                st.error("Passwords don't match!")
            else:
                if create_user(username, password, email):
                    st.success("Account created successfully!")
                    st.switch_page("pages/login.py")
                else:
                    st.error("Username or email already exists!")
        else:
            st.warning("Please fill in all fields")

with col2:
    if st.button("Back to Home", use_container_width=True):
        st.switch_page("pages/home.py")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown('<p class="login-text">Already have an account?</p>', unsafe_allow_html=True)

if st.button("Login Here", use_container_width=True):
    st.switch_page("pages/login.py")

st.markdown('</div>', unsafe_allow_html=True)
import streamlit as st

def show_landing_page():
    st.set_page_config(page_title="TextSum", layout="wide")
    # Add this CSS at the top of your home.py file after the imports
    st.markdown("""
    <style>
        /* Remove default Streamlit white background and padding */
        .stApp {
            background: transparent;
        }
        
        .block-container {
            padding: 0rem !important;
            margin-top: 4rem !important;
            margin-bottom: 4rem!important;
            padding-left : 2rem
        }
        
        [data-testid="stHeader"] {
            display: none !important;
        }
        
        [data-testid="stToolbar"] {
            display: none !important;
        }
        
        [data-testid="stDecoration"] {
            display: none !important;
        }
        
        #MainMenu {
            display: none !important;
        }
        
        footer {
            display: none !important;
        }
        
        section[data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
        }
    </style>
    """, unsafe_allow_html=True)
    # Add this CSS at the top of your home.py file after the imports
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        
        * {
            font-family: 'Inter', sans-serif;
        }

        .gradient-text {
            font-size: 2.8rem;
            font-weight: 800;
            line-height: 1.2;
            background: linear-gradient(45deg, #0066ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: fadeIn 1s ease-in;
            margin-bottom: 5rem;  /* Changed from 20px to 4rem */
            animation: slideUp 1s ease-out;
        }

        .subtitle {
            font-size: 1.05rem;
            color: #4B5563;
            margin: 25px 0;
            line-height: 1.8;
            animation: slideUp 1s ease-out;
        }

        .feature-card {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
            margin: 15px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: fadeIn 1s ease-in;
            height: 400px;  /* Added fixed height */
            display: flex;
            flex-direction: column;
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .feature-icon {
            font-size: 2.8em;
            color: #4A5568;
            margin-bottom: 15px;
            animation: pulse 2s infinite;
        }

        .feature-card h3 {
            margin-bottom: 12px;
            flex-shrink: 0;
        }
        
        .feature-card p {
            flex-grow: 1;
            overflow-y: auto;
            font-size: 1rem;
            line-height: 1.5;
        }

        .robot-container {
            display: flex;
            justify-content: flex-start;  /* Changed from center to flex-start */
            align-items: center;
            animation: float 3s ease-in-out infinite;
            margin-left: 20px;  /* Added margin for better spacing */
        }

        .robot-gif {
            max-width: 300px;  /* Slightly reduced for better alignment */
            height: auto;
            border-radius: 25px;
        }

        .button-container {
            display: flex;
            gap: 15px;
            margin-top: 25px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            animation: slideUp 1s ease-out;
        }

        .button-row {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }

        .button-row .stButton button {
            background: #0066ff;
            color: white;
            border: none;
            border-radius: 12px;
            padding: 15px 30px;
            font-size: 1.1rem;
            font-weight: 600;
            width: 100%;
            transition: all 0.3s ease;
            animation: buttonPop 0.3s ease-out;
}


        .stButton button:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            background: #0052cc;
        }

        @keyframes buttonPop {
            0% { transform: scale(0.95); }
            70% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes slideUp {
            from { 
                opacity: 0;
                transform: translateY(20px);
            }
            to { 
                opacity: 1;
                transform: translateY(0);
            }
        }

        h3 {
            font-size: 1.3rem;
            margin-bottom: 12px;
            color: #2D3748;
        }

        p {
            font-size: 1.05rem;
            color: #4A5568;
            line-height: 1.6;
        }

        .center-heading {
            text-align: center;
            font-size: 2rem;
            font-weight: 700;
            color: #1F2937;
            margin-top: 40px;
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown('<div class="gradient-text">Simplify Complex Content with AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Transform lengthy documents into clear, concise summaries. Our AI-powered platform helps you extract key information quickly and efficiently.</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Sign Up", key="signup_btn", use_container_width=True):
                st.switch_page("pages/signup.py")
        with col_btn2:
            if st.button("Login", key="login_btn", use_container_width=True):
                st.switch_page("pages/login.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="robot-container">', unsafe_allow_html=True)
        st.image(r"assets/bgrobot.gif", width=800)
        st.markdown('</div>', unsafe_allow_html=True)

    # Centered "Powerful Features"
    st.markdown('<div class="center-heading">Powerful Features</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #4B5563; font-size: 1.3rem; margin-bottom: 40px;">Our tool offers a comprehensive suite of features to make your summarization workflow smooth and efficient.</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📄</div>
            <h3>Multiple Input Options</h3>
            <p>Easily upload PDFs, screenshots (image-to-text), CSV files, or paste text directly to get instant summaries from any format.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3>AI Model Selection</h3>
            <p>Choose between precise extractive summaries or more human-like abstractive summaries, tailored to your needs.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚙️</div>
            <h3>Advanced Customization</h3>
            <p>Customize summary length, listen to your summaries with our built-in text-to-speech feature and download both audio and text summaries for easy access anytime.</p>
        </div>
        """, unsafe_allow_html=True)

# Initialize page state
if 'page' not in st.session_state:
    st.session_state.page = 'home'

show_landing_page()

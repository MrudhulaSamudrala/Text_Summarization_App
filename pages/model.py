import streamlit as st
import pandas as pd
from summarizer import Summarizer
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
from gtts import gTTS
import base64
import os
import tempfile
from datetime import datetime
import easyocr
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
from custom_attention import AttentionLayer

# Check if user is logged in
if 'logged_in' not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to access this page")
    st.switch_page("main.py")

# Display logout button in sidebar
with st.sidebar:
    st.write(f"Logged in as: **{st.session_state.username}**")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.switch_page("main.py")

# Initialize the BERT summarizer for extractive summarization
extractive_model = Summarizer(model='bert-base-uncased', gpu_id=-1)  # Force CPU usage

# Initialize session state for history
if 'summary_history' not in st.session_state:
    st.session_state.summary_history = []

# Load abstractive model components
@st.cache_resource
def load_abstractive_models():
    try:
        # Load tokenizers
        with open('Models/x_tokenizer.pickle', 'rb') as handle:
            x_tokenizer = pickle.load(handle)
        with open('Models/y_tokenizer.pickle', 'rb') as handle:
            y_tokenizer = pickle.load(handle)

        # Load max lengths
        max_text_len = int(np.load('Models/max_text_len.npy'))
        max_summary_len = int(np.load('Models/max_summary_len.npy'))

        # Load models
        encoder_model = load_model('Models/encoder_model1.h5', custom_objects={'AttentionLayer': AttentionLayer})
        decoder_model = load_model('Models/decoder_model1.h5', custom_objects={'AttentionLayer': AttentionLayer})

        return {
            'x_tokenizer': x_tokenizer,
            'y_tokenizer': y_tokenizer,
            'max_text_len': max_text_len,
            'max_summary_len': max_summary_len,
            'encoder_model': encoder_model,
            'decoder_model': decoder_model
        }
    except Exception as e:
        st.error(f"Error loading abstractive models: {e}")
        return None

# Load abstractive models
abstractive_models = load_abstractive_models()

def decode_sequence(input_seq, models):
    """Decodes sequence using trained seq2seq model."""
    if not models:
        return "Abstractive model not available"
    
    e_out, e_h, e_c = models['encoder_model'].predict(input_seq)
    target_seq = np.zeros((1, 1))
    target_seq[0, 0] = models['y_tokenizer'].word_index.get('sostok', 0)
    
    stop_condition = False
    decoded_sentence = ''
    while not stop_condition:
        output_tokens, h, c = models['decoder_model'].predict([target_seq] + [e_out, e_h, e_c])
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_token = models['y_tokenizer'].index_word.get(sampled_token_index, '')

        if sampled_token and sampled_token != 'eostok':
            decoded_sentence += ' ' + sampled_token

        if sampled_token == 'eostok' or len(decoded_sentence.split()) >= (models['max_summary_len'] - 1):
            stop_condition = True

        target_seq = np.zeros((1, 1))
        target_seq[0, 0] = sampled_token_index
        e_h, e_c = h, c

    return decoded_sentence.strip()

def text_cleaner(text):
    """Basic text preprocessing for abstractive summarization."""
    text = text.lower()
    text = ''.join([char for char in text if char.isalnum() or char.isspace()])
    return text.strip()

def summarize_text_abstractive(text, models):
    """Generate abstractive summary using the seq2seq model."""
    if not models:
        return "Abstractive model not available"
    
    try:
        text = text_cleaner(text)
        seq = models['x_tokenizer'].texts_to_sequences([text])
        padded_seq = pad_sequences(seq, maxlen=models['max_text_len'], padding='post')
        summary = decode_sequence(padded_seq.reshape(1, models['max_text_len']), models)
        return summary
    except Exception as e:
        return f"Error in abstractive summarization: {e}"

def summarize_text(text, ratio=0.3, model_type="extractive"):
    """Generate a summary from the given text using the selected model type."""
    if model_type == "extractive":
        summary = extractive_model(text, ratio=ratio)
        return "".join(summary)
    else:  # abstractive
        summary = summarize_text_abstractive(text, abstractive_models)
        # Ensure the summary is a valid string
        return str(summary) if summary else "No summary generated."

def add_to_history(original_text, summary, source_type):
    """Add a summary to the history."""
    # Create a descriptive title based on the source type and content
    if source_type == "Text Input":
        title = f"{original_text[:50]}..."
    elif source_type == "PDF":
        title = f"PDF document: {original_text[:50]}..."
    elif source_type == "Image":
        title = f"Image text: {original_text[:50]}..."
    else:  # CSV
        title = f"CSV entry: {original_text[:50]}..."
    
    st.session_state.summary_history.append({
        'title': title,
        'source_type': source_type,
        'original_text': original_text[:100] + "..." if len(original_text) > 100 else original_text,
        'summary': summary
    })

def clear_history():
    """Clear the summary history."""
    st.session_state.summary_history = []

def text_to_speech(text, lang='en'):
    """Convert text to speech and return the audio file path and data."""
    try:
        if not text or not isinstance(text, str):
            return None, None
            
        # Create temp_audio directory if it doesn't exist
        temp_dir = os.path.join(os.getcwd(), 'temp_audio')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        audio_file = os.path.join(temp_dir, f'summary_{timestamp}.mp3')
        
        # Generate and save audio
        tts = gTTS(text=text, lang=lang)
        tts.save(audio_file)
        
        # Read the audio data
        with open(audio_file, 'rb') as f:
            audio_data = f.read()
        
        return audio_file, audio_data
    except Exception as e:
        st.error(f"Error generating audio: {str(e)}")
        return None, None

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file using PyMuPDF."""
    doc = None
    tmp_file_path = None
    try:
        # Create a temporary file to store the uploaded PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_file.getvalue())
            tmp_file_path = tmp_file.name

        # Open the PDF with PyMuPDF
        doc = fitz.open(tmp_file_path)
        text = ""
        
        # Extract text from each page
        for page_num, page in enumerate(doc):
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.get_text()
        
        return text.strip() if text else "No text extracted from PDF."
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"
    finally:
        # Clean up resources
        if doc:
            doc.close()
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.unlink(tmp_file_path)
            except Exception as e:
                st.warning(f"Could not delete temporary file: {str(e)}")

def extract_text_from_image(image_file):
    """Extract text from an image file using EasyOCR with Tesseract as fallback."""
    try:
        # Initialize EasyOCR reader (only once)
        if 'reader' not in st.session_state:
            st.session_state.reader = easyocr.Reader(['en'])
        
        # Convert the uploaded file to an image
        image = Image.open(image_file)
        # Convert PIL Image to numpy array
        image_np = np.array(image)
        
        # Try EasyOCR first
        try:
            results = st.session_state.reader.readtext(image_np)
            # Extract text from results
            text = ' '.join([result[1] for result in results])
            if text.strip():
                return text.strip()
        except Exception as e:
            st.warning(f"EasyOCR failed, falling back to Tesseract: {str(e)}")
        
        # Fallback to Tesseract if EasyOCR fails or returns no text
        text = pytesseract.image_to_string(image)
        return text.strip() if text else "No text extracted from image."
        
    except Exception as e:
        return f"Error extracting text from image: {str(e)}"

def extract_text_from_csv(csv_file):
    """Extract text from a CSV file."""
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        # Check if 'Text' column exists
        if 'Text' not in df.columns:
            # Try to find a suitable column for text extraction
            text_columns = [col for col in df.columns if df[col].dtype == 'object' and df[col].str.len().mean() > 20]
            if text_columns:
                # Use the column with the longest average text length
                text_column = max(text_columns, key=lambda x: df[x].str.len().mean())
                df['Text'] = df[text_column]
            else:
                return "No suitable text column found in CSV. Please ensure your CSV has a 'Text' column or a column containing substantial text."
        
        # Remove rows with missing text
        df = df.dropna(subset=['Text'])
        
        # Combine all text with proper formatting
        combined_text = ""
        for idx, row in df.iterrows():
            combined_text += f"\n--- Entry {idx + 1} ---\n"
            combined_text += str(row['Text']) + "\n"
        
        return combined_text.strip() if combined_text else "No text extracted from CSV."
    except Exception as e:
        return f"Error extracting text from CSV: {str(e)}"

# Streamlit UI
st.title("TextSum App")

# Welcome message
st.write(f"Welcome back, {st.session_state.username}!")

# Model selection
model_type = st.radio(
    "Select Summarization Model",
    ["Extractive", "Abstractive"],
    help="Extractive: Selects important sentences from the text. Abstractive: Generates new sentences."
)

# Initialize session state for audio control
if 'current_audio_file' not in st.session_state:
    st.session_state.current_audio_file = None

# Create tabs for different input methods
tab1, tab2, tab3, tab4 = st.tabs(["Text Input", "PDF Upload", "Image Upload", "CSV Upload"])

def display_summary_with_audio(summary, unique_id=None):
    """Display summary with audio controls."""
    st.write(summary)
    
    # Generate new audio file for each summary
    audio_path, audio_data = text_to_speech(summary)
    if audio_path and audio_data:
        st.audio(audio_data, format='audio/mp3')
        
        # Generate a timestamp for unique keys
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        
        col1, col2, col3 = st.columns([4, 4, 2])
        with col1:
            st.download_button(
                label="📥 Audio Summary",
                data=audio_data,
                file_name=os.path.basename(audio_path),
                mime="audio/mp3",
                key=f"audio_download_{unique_id or timestamp}"
            )
        with col2:
            st.download_button(
                label="📥 Text Summary",
                data=summary,
                file_name=f"summary_{timestamp}.txt",
                mime="text/plain",
                key=f"text_download_{unique_id or timestamp}"
            )
        with col3:
            if st.button("New Summary", key=f"new_summary_{unique_id or timestamp}"):
                if audio_path:
                    try:
                        os.remove(audio_path)
                    except:
                        pass
                st.session_state.clear_summary = True
                st.rerun()

    # Clean up the temporary file
    try:
        os.remove(audio_path)
    except:
        pass

with tab1:
    st.subheader("Enter Text for Summarization")
    user_input = st.text_area("Type your text here:")
    
    # Summary length slider (only for extractive model)
    if model_type == "Extractive":
        summary_ratio = st.slider(
            "Summary Length",
            min_value=0.1,
            max_value=0.9,
            value=0.3,
            step=0.1,
            help="Adjust the length of the summary. Higher values will result in longer summaries.",
            key="text_slider"
        )
    else:
        summary_ratio = 0.3  # Default value for abstractive
    
    if st.button("Summarize Text", key="text_button"):
        if user_input.strip():
            summary = summarize_text(user_input, ratio=summary_ratio, model_type=model_type.lower())
            st.subheader("Summary:")
            display_summary_with_audio(summary)
            add_to_history(user_input, summary, f"Text Input ({model_type})")
        else:
            st.warning("Please enter some text to summarize.")

with tab2:
    st.subheader("Upload PDF")
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"], key="pdf_uploader")
    
    if pdf_file is not None:
        # Summary length slider
        summary_ratio = st.slider(
            "Summary Length",
            min_value=0.1,
            max_value=0.9,
            value=0.3,
            step=0.1,
            help="Adjust the length of the summary. Higher values will result in longer summaries.",
            key="pdf_slider"
        )
        
        if st.button("Extract and Summarize", key="pdf_button"):
            text = extract_text_from_pdf(pdf_file)
            st.subheader("Extracted Text:")
            st.write(text)
            if text and text != "No text extracted from PDF.":
                summary = summarize_text(text, ratio=summary_ratio, model_type=model_type.lower())
                st.subheader("Summary:")
                display_summary_with_audio(summary)
                add_to_history(text, summary, f"PDF ({model_type})")
            else:
                st.warning("No valid text found in PDF.")

with tab3:
    st.subheader("Upload Image")
    image_file = st.file_uploader("Upload an image file", type=["png", "jpg", "jpeg"], key="image_uploader")
    
    if image_file is not None:
        st.image(image_file, caption="Uploaded Image", use_container_width=True)
        # Summary length slider
        summary_ratio = st.slider(
            "Summary Length",
            min_value=0.1,
            max_value=0.9,
            value=0.3,
            step=0.1,
            help="Adjust the length of the summary. Higher values will result in longer summaries.",
            key="image_slider"
        )
        
        if st.button("Extract and Summarize", key="image_button"):
            text = extract_text_from_image(image_file)
            st.subheader("Extracted Text:")
            st.write(text)
            if text and text != "No text extracted from image.":
                summary = summarize_text(text, ratio=summary_ratio, model_type=model_type.lower())
                st.subheader("Summary:")
                display_summary_with_audio(summary)
                add_to_history(text, summary, f"Image ({model_type})")
            else:
                st.warning("No valid text found in image.")

with tab4:
    st.subheader("Upload CSV File")
    csv_file = st.file_uploader("Upload a CSV file with a 'Text' column", type=["csv"], key="csv_uploader")

    if csv_file is not None:
        # Summary length slider (only for extractive model)
        if model_type == "Extractive":
            summary_ratio = st.slider(
                "Summary Length",
                min_value=0.1,
                max_value=0.9,
                value=0.3,
                step=0.1,
                help="Adjust the length of the summary. Higher values will result in longer summaries.",
                key="csv_slider"
            )
        else:
            summary_ratio = 0.3  # Default value for abstractive
        
        # Add option to extract text from CSV
        extract_option = st.radio(
            "CSV Processing Option",
            ["Process as CSV (Summarize each row)", "Extract text from CSV (Summarize as a whole)"],
            help="Choose how to process the CSV file"
        )
        
        if extract_option == "Process as CSV (Summarize each row)":
            df = pd.read_csv(csv_file)
    
            if 'Text' in df.columns:
                df = df.dropna(subset=['Text'])  # Remove rows with missing text
                # Add row numbers and generate summaries
                df['Row_Number'] = range(1, len(df) + 1)
                df['Summary'] = df['Text'].apply(lambda x: summarize_text(x, ratio=summary_ratio, model_type=model_type.lower()))
                st.subheader("Summarized Data")
        
                # Display each summary with audio controls
                for idx, row in df.iterrows():
                    st.write(f"Row {row['Row_Number']}:")
                    st.write("Original Text:")
                    st.write(row['Text'])
                    st.write("Summary:")
                    display_summary_with_audio(row['Summary'], f"csv_row_{row['Row_Number']}")
                    add_to_history(row['Text'], row['Summary'], f"CSV Row {row['Row_Number']} ({model_type})")
                    st.markdown("---")
                
                # Option to download the summarized file
                #st.download_button("Download Summary", csv, "summary.csv", "text/csv")
            else:
                st.error("CSV file must contain a 'Text' column.")
        else:
            # Extract text from CSV and summarize as a whole
            if st.button("Extract and Summarize", key="csv_extract_button"):
                text = extract_text_from_csv(csv_file)
                st.subheader("Extracted Text:")
                st.write(text)
                if text and text != "No text extracted from CSV." and not text.startswith("Error"):
                    summary = summarize_text(text, ratio=summary_ratio, model_type=model_type.lower())
                    st.subheader("Summary:")
                    display_summary_with_audio(summary)
                    add_to_history(text, summary, f"CSV Extract ({model_type})")
                else:
                    st.warning(text)

# Sidebar with history and new chat button
with st.sidebar:
    st.header("Summary History")
    
    # New Chat button
    if st.button("New Chat", type="primary"):
        clear_history()
        st.success("History cleared! Start a new chat.")
    
    # Display history
    if st.session_state.summary_history:
        for entry in reversed(st.session_state.summary_history):
            with st.expander(f"📝 {entry['source_type']}"):
                st.write("**Original Text:**")
                st.write(entry['original_text'])
                st.write("**Summary:**")
                st.write(entry['summary'])
                
                # Generate audio for the summary
                # In the sidebar history section
                audio_file, audio_data = text_to_speech(entry['summary'])
                if audio_file and audio_data:
                    st.audio(audio_data, format='audio/mp3')
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Audio",
                            data=audio_data,
                            file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                            mime="audio/mpeg",
                            key=f"audio_{entry['source_type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        )
                    with col2:
                        st.download_button(
                            label="📄 Text",
                            data=entry['summary'],
                            file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            key=f"text_{entry['source_type']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        )
                
                # Clean up temporary audio file
                try:
                    os.remove(audio_file)
                except:
                    pass
    else:
        st.info("No summary history yet. Start by summarizing some text!")






                
                

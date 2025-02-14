import streamlit as st
import os
import tempfile
from faster_whisper import WhisperModel
from googletrans import Translator
from gtts import gTTS
from PIL import Image
from streamlit_extras.add_vertical_space import add_vertical_space

# Define color themes
color_themes = {
    "Sunset Glow": ["#ff9a9e", "#fad0c4", "#fad0c4", "#ffdde1", "#ffc3a0"],
    "Ocean Breeze": ["#00c6fb", "#005bea", "#00c6fb", "#005bea", "#a8c0ff"],
    "Forest Mist": ["#d4fc79", "#96e6a1", "#d4fc79", "#96e6a1", "#11998e"],
    "Midnight Sky": ["#232526", "#414345", "#232526", "#414345", "#1e3c72"],
    "Royal Elegance": ["#141e30", "#243b55", "#141e30", "#243b55", "#3a6073"]
}

# Streamlit UI Configuration
st.set_page_config(page_title="🎙️ Advanced Transcription & Translation", layout="wide")

# Color theme selection
theme_choice = st.selectbox("🎨 Select a Theme", list(color_themes.keys()))
selected_colors = color_themes[theme_choice]

# Apply gradient styling
st.markdown(
    f"""
    <style>
        body {{
            background: linear-gradient(45deg, {', '.join(selected_colors)});
        }}
        .stApp {{
            background: linear-gradient(45deg, {', '.join(selected_colors)});
            color: white;
        }}
        .stButton>button {{
            background: {selected_colors[3]};
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 16px;
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            background: {selected_colors[4]};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🎧 Advanced Audio Transcription & Translation")
st.markdown("Enhanced UI with beautiful gradients, animations, and smooth interactivity.")

# Upload audio file
uploaded_audio = st.file_uploader("📂 Upload an audio file", type=["mp3", "wav", "m4a"], help="Supported formats: MP3, WAV, M4A")

# Language selection for translation
languages = {
    "English": "en", "Urdu": "ur", "French": "fr", "Spanish": "es", "German": "de",
    "Chinese (Simplified)": "zh-cn", "Arabic": "ar", "Hindi": "hi", "Russian": "ru",
    "Portuguese": "pt", "Japanese": "ja", "Korean": "ko", "Italian": "it", "Turkish": "tr"
}
selected_language = st.selectbox("🌎 Select a language for translation", list(languages.keys()))

if uploaded_audio:
    with st.spinner("🔄 Processing audio... Please wait."):
        # Save uploaded file temporarily
        temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
        with open(temp_audio_path, "wb") as f:
            f.write(uploaded_audio.read())
        
        # Transcription Process
        model = WhisperModel("small", compute_type="int8")
        segments, _ = model.transcribe(temp_audio_path)
        transcript = "\n".join(segment.text for segment in segments)
    
    # Display transcript
    st.subheader("📝 Generated Transcript:")
    st.text_area("Transcript", transcript, height=200)

    if st.button("Translate Transcript", key="translate_btn"):
        with st.spinner(f"🔄 Translating to {selected_language}..."):
            translator = Translator()
            translated_text = translator.translate(transcript, dest=languages[selected_language]).text
            st.subheader(f"🌍 Translated Transcript ({selected_language}):")
            st.text_area("Translation", translated_text, height=200)
        
        with st.spinner("🎙️ Generating translated speech..."):
            temp_audio_path = text_to_speech(translated_text, languages[selected_language])
            st.audio(temp_audio_path, format="audio/mp3")
            st.download_button("📥 Download Translated Speech", open(temp_audio_path, "rb"), file_name="translated_audio.mp3", mime="audio/mp3")
    
    # Download buttons
    st.download_button("📥 Download Transcript", transcript, file_name="transcript.txt")
    st.download_button(f"📥 Download Translation ({selected_language})", translated_text, file_name="translation.txt")

st.markdown("---")
st.caption("🚀 Built with Streamlit, Faster-Whisper & Google Translate API")
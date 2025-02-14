import streamlit as st
import os
import tempfile
import yt_dlp
from faster_whisper import WhisperModel
from googletrans import Translator
from gtts import gTTS
from streamlit_extras.add_vertical_space import add_vertical_space

# Define color themes
color_themes = {
    "Sunset Glow": ["#ff9a9e", "#fad0c4", "#ffdde1"],
    "Ocean Breeze": ["#00c6fb", "#005bea", "#a8c0ff"],
    "Forest Mist": ["#d4fc79", "#96e6a1", "#11998e"],
    "Midnight Sky": ["#232526", "#414345", "#1e3c72"],
    "Royal Elegance": ["#141e30", "#243b55", "#3a6073"]
}

# Streamlit UI Configuration
st.set_page_config(page_title="🎙️ Transcription & Translation", layout="wide")

# Theme Selection
theme_choice = st.selectbox("🎨 Select a Theme", list(color_themes.keys()))
selected_colors = color_themes[theme_choice]

st.markdown(
    f"""
    <style>
        body {{background: linear-gradient(45deg, {', '.join(selected_colors)});}}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🎧 Audio Transcription with Translation")
add_vertical_space(1)

# Input Options
uploaded_file = None
youtube_url = None

data_source = st.radio("Select input type:", ["Upload Audio", "YouTube Video URL"])

if data_source == "Upload Audio":
    uploaded_file = st.file_uploader("📂 Upload an audio file", type=["mp3", "wav", "m4a"])
elif data_source == "YouTube Video URL":
    youtube_url = st.text_input("📺 Enter YouTube Video URL")

# Language Selection
languages = {"English": "en", "Urdu": "ur", "French": "fr", "Spanish": "es", "German": "de"}
selected_language = st.selectbox("🌎 Select a language for translation", list(languages.keys()))

# Processing
if uploaded_file is not None or (youtube_url and youtube_url.strip()):
    with st.spinner("🔄 Processing..."):
        try:
            if data_source == "YouTube Video URL" and youtube_url.strip():
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': '%(title)s.%(ext)s',
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(youtube_url, download=True)
                    audio_path = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".mp4", ".mp3")
            elif uploaded_file is not None:
                temp_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.read())
                audio_path = temp_file_path
            else:
                st.error("❌ Please provide a valid YouTube URL or upload an audio file.")
                st.stop()

            # Transcription
            model = WhisperModel("small", compute_type="int8")
            segments, _ = model.transcribe(audio_path)
            transcript = "\n".join(segment.text for segment in segments)
            st.subheader("📝 Generated Transcript:")
            st.text_area("Transcript", transcript, height=200)

            if st.button("Translate Transcript"):
                translator = Translator()
                translated_text = translator.translate(transcript, dest=languages[selected_language]).text
                st.subheader(f"🌍 Translated Transcript ({selected_language}):")
                st.text_area("Translation", translated_text, height=200)

                with st.spinner("🎙️ Generating translated speech..."):
                    tts = gTTS(translated_text, lang=languages[selected_language])
                    translated_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                    tts.save(translated_audio_path)
                    st.audio(translated_audio_path, format="audio/mp3")
                    st.download_button("📥 Download Translated Speech", open(translated_audio_path, "rb"), file_name="translated_audio.mp3", mime="audio/mp3")

            # Download options
            st.download_button("📥 Download Transcript", transcript, file_name="transcript.txt")
            st.download_button(f"📥 Download Translation ({selected_language})", translated_text, file_name="translation.txt")

        except Exception as e:
            st.error(f"⚠️ An error occurred: {e}")

st.markdown("---")
st.caption("🚀 Built with Streamlit, Faster-Whisper, Google Translate API & yt-dlp")

import streamlit as st
import os
import tempfile
import whisper
import yt_dlp
from googletrans import Translator
from gtts import gTTS

# Ensure Whisper Model is Downloaded
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")

model = load_whisper_model()
translator = Translator()

def download_youtube_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        'outtmpl': 'downloaded_audio.%(ext)s'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            return 'downloaded_audio.mp3'
        except Exception as e:
            st.error(f"Error downloading video: {e}")
            return None

def transcribe_audio(file_path):
    if not os.path.exists(file_path):
        st.error("Audio file not found!")
        return None
    result = model.transcribe(file_path)
    return result.get('text', "")

def translate_text(text, target_lang):
    try:
        translated = translator.translate(text, dest=target_lang)
        return translated.text
    except Exception as e:
        st.error(f"Translation Error: {e}")
        return None

def text_to_speech(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save("translated_audio.mp3")
        return "translated_audio.mp3"
    except Exception as e:
        st.error(f"TTS Error: {e}")
        return None

# Streamlit UI
st.title("🎙️ Audio Transcription & Translation")

option = st.radio("Choose an option:", ("Paste YouTube URL", "Upload Audio File"))

file_path = None
if option == "Paste YouTube URL":
    youtube_url = st.text_input("Enter YouTube URL:")
    if youtube_url and st.button("Download & Process"):
        with st.spinner("Downloading..."):
            file_path = download_youtube_audio(youtube_url)
            if file_path:
                st.session_state['file_path'] = file_path
                st.success("Download complete!")

elif option == "Upload Audio File":
    uploaded_file = st.file_uploader("Upload your audio file", type=["mp3", "wav", "m4a"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(uploaded_file.read())
            file_path = temp_file.name
            st.session_state['file_path'] = file_path

if 'file_path' in st.session_state and st.button("Generate Transcript"):
    with st.spinner("Processing audio..."):
        transcript = transcribe_audio(st.session_state['file_path'])
        if transcript:
            st.session_state['transcript'] = transcript
            st.success("Transcription complete!")
            st.text_area("Transcript:", transcript, height=200)

if 'transcript' in st.session_state:
    st.subheader("Translate Transcript")
    languages = {"English": "en", "French": "fr", "Spanish": "es", "German": "de", "Urdu": "ur"}
    selected_lang = st.selectbox("Select Language:", list(languages.keys()))

    if st.button("Translate"):
        with st.spinner("Translating..."):
            translated_text = translate_text(st.session_state['transcript'], languages[selected_lang])
            if translated_text:
                st.session_state['translated_text'] = translated_text
                st.success("Translation complete!")
                st.text_area("Translated Text:", translated_text, height=200)

if 'translated_text' in st.session_state:
    st.subheader("Generate Audio")
    if st.button("Generate Audio"):
        with st.spinner("Generating audio..."):
            audio_file = text_to_speech(st.session_state['translated_text'], languages[selected_lang])
            if audio_file:
                st.success("Audio generation complete!")
                st.audio(audio_file, format='audio/mp3')

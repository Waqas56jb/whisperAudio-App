import streamlit as st
import os
import tempfile
import whisper
import yt_dlp
from googletrans import Translator
from gtts import gTTS

# Load Whisper Model
model = whisper.load_model("base")
translator = Translator()

def download_youtube_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'downloaded_audio.%(ext)s'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return 'downloaded_audio.mp3'

def transcribe_audio(file_path):
    result = model.transcribe(file_path)
    return result['text']

def translate_text(text, target_lang):
    translated = translator.translate(text, dest=target_lang)
    return translated.text

def text_to_speech(text, lang):
    tts = gTTS(text=text, lang=lang)
    tts.save("translated_audio.mp3")
    return "translated_audio.mp3"

# Streamlit UI
st.title("🎙️ Audio Transcription & Translation")

option = st.radio("Choose an option:", ("Paste YouTube URL", "Upload Audio File"))

file_path = None
if option == "Paste YouTube URL":
    youtube_url = st.text_input("Enter YouTube URL:")
    if youtube_url:
        with st.spinner("Downloading and processing..."):
            file_path = download_youtube_audio(youtube_url)
            st.session_state['file_path'] = file_path
            st.success("Download complete! Now generate transcript.")
        if st.button("Generate Transcript"):
            with st.spinner("Processing audio..."):
                transcript = transcribe_audio(st.session_state['file_path'])
                st.session_state['transcript'] = transcript
                st.success("Transcription complete!")
                st.text_area("Transcript:", transcript, height=200)

elif option == "Upload Audio File":
    uploaded_file = st.file_uploader("Upload your audio file", type=["mp3", "wav", "m4a"])
    if uploaded_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(uploaded_file.read())
            file_path = temp_file.name
        if st.button("Generate Transcript"):
            with st.spinner("Processing audio..."):
                transcript = transcribe_audio(file_path)
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
            st.session_state['translated_text'] = translated_text
            st.success("Translation complete!")
            st.text_area("Translated Text:", translated_text, height=200)

if 'translated_text' in st.session_state:
    st.subheader("Generate Audio")
    if st.button("Generate Audio"):
        with st.spinner("Generating audio..."):
            audio_file = text_to_speech(st.session_state['translated_text'], languages[selected_lang])
            st.success("Audio generation complete!")
            st.audio(audio_file, format='audio/mp3')

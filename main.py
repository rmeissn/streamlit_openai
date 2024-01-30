from openai import OpenAI
import streamlit as st
import tempfile
import os

st.set_page_config(layout="wide")
st.title('Whisper Audio Transcription')

api_key = st.text_input("OpenAI API Key:", value=None)

file = st.file_uploader("Audio-File", type=['m4a', 'mp3', 'webm', 'mp4', 'mpga', 'wav', 'mpeg'], help="File must be less than 25MB")

language = st.selectbox("Language:", ['de', 'en'])

def transcribe_audio(api_key, audio_file, language):
  file_extension = os.path.splitext(audio_file.name)[-1]
  
  tmp = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
  with tmp as temp_audio_file:
    temp_audio_file.write(audio_file.read())
    temp_audio_file.seek(0)  # Move the file pointer to the beginning of the file
    
  print (tmp.name)
  audio = open(tmp.name, "rb")
  client = OpenAI(api_key=api_key)
  transcript = client.audio.transcriptions.create(model="whisper-1", file=audio, language=language)
  try:
    audio.close()
    tmp.close()
    os.unlink(tmp.name)
  except:
    print("Problem unlinking file")
  return transcript

if st.button('Transcribe') and api_key is not None and file:
  with st.spinner('Processing...'):
    transcript = transcribe_audio(api_key, file, language)
    st.write(transcript.text)

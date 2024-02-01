from openai import OpenAI
import streamlit as st
import tempfile
import os

api_key = ""

st.set_page_config(layout="wide")
st.title("OpenAI Tooling")

with st.sidebar:
    st.title("General Settings")
    api_key = st.text_input("OpenAI API Key:", value="", type="password")

client = None
if api_key != "":
    client = OpenAI(api_key=api_key)

tab1, tab2, tab3 = st.tabs(["Speech to Text", "Text to Speech", "Image Generation"])

with tab1:
    st.header("Whisper Audio Transcription")
    file = st.file_uploader(
        "Audio-File",
        type=["flac", "mp3", "mp4", "mpeg", "mpga", "m4a", "ogg", "wav", "webm"],
        help="File must be less than 24MB",
    )

    languages = {"German": "de", "English": "en", "French": "fr", "Italien": "it"}
    selected_language = st.selectbox("Language:", languages.keys())
    language = languages[selected_language]

    optional_prompt = st.text_input(
        "Optional Prompt",
        help="An optional text to guide the model's style or continue a previous audio segment. The prompt should match the audio language (e.g. English prompt for English audio).",
    )

    if st.button(
        "Transcribe", disabled=api_key == "" or file is None, key="transcribe"
    ):
        with st.spinner("Processing..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", file=file, language=language, prompt=optional_prompt
            )
            st.download_button(
                label="Download Transcript",
                data=transcript.text,
                file_name="transcript.txt",
                mime="plain/text",
            )
            with st.expander("Show trancsript"):
                st.write(transcript.text)

with tab2:
    st.header("Whisper Text to Speech")

    selected_model = st.selectbox("Model:", ["Normal", "High Definition"])
    model = "tts-1"
    if selected_model != "Normal":
        model = "tts-1-hd"
    selected_voice = st.selectbox(
        "Voice:",
        ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        index=4,
        help="See examples at https://platform.openai.com/docs/guides/text-to-speech/voice-options",
    )
    input = st.text_area(
        "Text:",
        help="The text you'd like to turn into spoken words. Supports all languages listed at https://platform.openai.com/docs/guides/text-to-speech/supported-languages",
        max_chars=4096,
    )

    if st.button("Create", disabled=api_key == "" or input == "", key="tts"):
        with st.spinner("Processing..."):
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            response = client.audio.speech.create(
                model=model, voice=selected_voice, input=input
            )
            response.stream_to_file(tmp.name)
            audio_file = open(tmp.name, "rb")
            audio_bytes = audio_file.read()
            tmp.close()
            os.unlink(tmp.name)
            st.audio(audio_bytes, format="audio/mp3")
            st.download_button(
                label="Download Audio File",
                data=audio_bytes,
                file_name="spoken_text.mp3",
                mime="audio/mp3",
            )

with tab3:
    st.header("Image Generation")

    selected_model = st.selectbox("Model:", ["dall-e-3"])
    size = st.selectbox(
        "Size:",
        ["1024x1024", "1792x1024", "1024x1792"],
    )
    quality = st.selectbox(
        "Quality:",
        ["standard", "hd"],
    )
    style = st.selectbox(
        "Style:",
        ["vivid", "natural"],
    )
    input = st.text_area("Prompt:", max_chars=4000)

    if st.button("Create", disabled=api_key == "" or input == "", key="image"):
        with st.spinner("Processing..."):
            response = client.images.generate(
                model=selected_model,
                prompt=input,
                size=size,
                quality=quality,
                style=style,
            )
            print(response)
            st.image(response.data[0].url, caption=input, width=int(size.split("x")[0]))

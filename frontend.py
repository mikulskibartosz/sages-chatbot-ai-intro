import streamlit as st
import requests
from audio.audio import text_to_speech, speech_to_text
from streamlit_mic_recorder import mic_recorder


def get_user_id():
    response = requests.get("http://localhost:5000/userid")
    return response.text


def ask_ai(new_message, user_id):
    response = requests.post("http://localhost:5000/chat", json={"message": new_message, "userId": user_id})
    response_json = response.json()

    return response_json["response"]


st.title("💬 AI Chatbot")
st.caption("🚀 Ask about the Titanic disaster")

if "user_id" not in st.session_state:
    st.session_state.user_id = get_user_id()
    st.text("User Id: " + st.session_state.user_id)
else:
    st.text("User Id: " + st.session_state.user_id)

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

with st.sidebar:
    wav_audio_data = mic_recorder(
        start_prompt="Start recording",
        stop_prompt="Stop recording",
        just_once=True,
    )


if prompt := st.chat_input() or wav_audio_data:
    if wav_audio_data:
        prompt = speech_to_text(wav_audio_data)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = ask_ai(prompt, st.session_state.user_id)
    st.chat_message("assistant").write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

    audio_bytes = text_to_speech(response, voice="alloy")
    st.audio(audio_bytes, format='audio/mpeg', autoplay=True)

import openai
from pathlib import Path
import tempfile
from io import BytesIO


def text_to_speech(text, voice):
    client = openai.OpenAI()

    with tempfile.TemporaryDirectory() as temp_dir:
        speech_file_path = Path(temp_dir) / "audio.mp3"
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        response.stream_to_file(speech_file_path)

        audio_file = open(speech_file_path, 'rb')
        audio_bytes = audio_file.read()
        audio_file.close()
        return audio_bytes
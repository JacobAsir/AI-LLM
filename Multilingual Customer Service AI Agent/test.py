
import os
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = Groq()
speech_file_path = Path(__file__).parent / "speech.wav"
response = client.audio.speech.create(
  model="playai-tts",
  voice="Aaliyah-PlayAI",
  response_format="wav",
  input="Make sure to put down your Japanese skills on your resume even if it's just N5. I meet so many engineers in Japan who can speak basic Japanese but leave it off their resume because its not good enough.",
)
response.write_to_file(speech_file_path)

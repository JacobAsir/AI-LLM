import os
import time
import threading
import tempfile
from pathlib import Path
import pygame
import pyaudio
import wave
import keyboard
import speech_recognition as sr
from gtts import gTTS
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq()

# Initialize pygame for audio playback
pygame.mixer.init()

# Global variables
conversation_history = []
recording = False
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
WAVE_OUTPUT_FILENAME = "audio.wav"
RECORD_SECONDS = 5  # Default recording time

# Create a lock for thread safety
lock = threading.Lock()

# Initialize speech recognizer
recognizer = sr.Recognizer()

def record_audio(duration=None):
    """
    Record audio from the microphone

    Args:
        duration (int, optional): Recording duration in seconds. If None, records until stopped.

    Returns:
        str: Path to the recorded audio file
    """
    global recording

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("\n🎤 Recording... Press 'q' to stop.")

    frames = []
    recording = True
    start_time = time.time()

    # Record until stopped or duration reached
    while recording:
        data = stream.read(CHUNK)
        frames.append(data)

        # Check if duration is set and reached
        if duration and (time.time() - start_time) > duration:
            recording = False

        # Check if 'q' key is pressed to stop recording
        if keyboard.is_pressed('q'):
            recording = False

    print("✅ Recording stopped.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Save the recorded audio to a file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return WAVE_OUTPUT_FILENAME

def transcribe_audio(audio_file):
    """
    Transcribe audio to text using SpeechRecognition

    Args:
        audio_file (str): Path to the audio file

    Returns:
        str: Transcribed text
    """
    print("🔄 Transcribing audio...")

    try:
        # Load the audio file
        with sr.AudioFile(audio_file) as source:
            # Record audio from the file
            audio_data = recognizer.record(source)

            # Use Google's speech recognition
            transcribed_text = recognizer.recognize_google(audio_data)
            print(f"📝 Transcription: {transcribed_text}")
            return transcribed_text

    except sr.UnknownValueError:
        print("❌ Speech Recognition could not understand audio")
        return "Sorry, I couldn't understand what you said."

    except sr.RequestError as e:
        print(f"❌ Speech Recognition service error: {str(e)}")
        return "Sorry, the speech recognition service is unavailable."

    except Exception as e:
        print(f"❌ Transcription error: {str(e)}")
        return "Sorry, I couldn't transcribe your audio."

def generate_response(text):
    """
    Generate a response using Groq's LLM

    Args:
        text (str): User input text

    Returns:
        str: Generated response
    """
    print("🤖 Generating response...")

    # Prepare conversation history for context
    messages = [
        {"role": "system", "content": "You are a helpful, friendly, and concise voice assistant. Provide clear and direct responses."}
    ]

    # Add conversation history (up to last 5 exchanges)
    for i in range(max(0, len(conversation_history) - 5), len(conversation_history)):
        role, content = conversation_history[i]
        messages.append({"role": role, "content": content})

    # Add current user message
    messages.append({"role": "user", "content": text})

    try:
        # Call the Groq API
        completion = client.chat.completions.create(
            model="llama3-70b-8192",  # Using a powerful model for high-quality responses
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )

        response_text = completion.choices[0].message.content
        print(f"💬 Response: {response_text}")

        # Add to conversation history
        with lock:
            conversation_history.append(("user", text))
            conversation_history.append(("assistant", response_text))

        return response_text

    except Exception as e:
        print(f"❌ Response generation error: {str(e)}")
        return "Sorry, I couldn't generate a response."

def text_to_speech(text):
    """
    Convert text to speech using gTTS

    Args:
        text (str): Text to convert to speech

    Returns:
        str: Path to the generated speech file
    """
    print("🔊 Converting text to speech...")

    speech_file_path = Path(__file__).parent / "speech.mp3"

    try:
        # Create gTTS object
        tts = gTTS(text=text, lang='en', slow=False)

        # Save to file
        tts.save(str(speech_file_path))
        print("✅ Speech generated successfully.")

        return str(speech_file_path)

    except Exception as e:
        print(f"❌ Text-to-speech error: {str(e)}")
        return None

def play_audio(audio_file):
    """
    Play audio file

    Args:
        audio_file (str): Path to the audio file
    """
    try:
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"❌ Audio playback error: {str(e)}")

def stop_recording():
    """Function to stop recording when 'q' is pressed"""
    global recording
    recording = False

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the application header"""
    clear_screen()
    print("=" * 50)
    print("🎙️  VOICE-TO-VOICE AI ASSISTANT 🔊")
    print("=" * 50)
    print("Options:")
    print("1. Voice mode (press 'r' to start recording, 'q' to stop)")
    print("2. Text mode (press 't' to type your message)")
    print("3. Exit (press 'e' to exit)")
    print("=" * 50)

def process_voice_input():
    """Process voice input in a separate thread to improve responsiveness"""
    audio_file = record_audio()

    # Process the audio
    transcribed_text = transcribe_audio(audio_file)

    if transcribed_text:
        # Generate response
        response_text = generate_response(transcribed_text)

        # Convert response to speech and play it
        speech_file = text_to_speech(response_text)

        if speech_file:
            play_audio(speech_file)

    # Reset for next interaction
    time.sleep(1)
    print_header()

def process_text_input(user_input):
    """Process text input in a separate thread to improve responsiveness"""
    if user_input.strip():
        # Generate response
        response_text = generate_response(user_input)

        # Convert response to speech and play it
        speech_file = text_to_speech(response_text)

        if speech_file:
            play_audio(speech_file)

    # Reset for next interaction
    time.sleep(1)
    print_header()

def main():
    """Main function to run the voice-to-voice assistant"""
    global recording

    print_header()

    # Simplified menu-based approach for easier interaction
    while True:
        print("\nChoose an option:")
        print("1. Voice mode")
        print("2. Text mode")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            # Voice mode
            print("\n🎤 Voice mode selected.")
            print("Recording will start. Press 'q' to stop when done speaking.")
            input("Press Enter to start recording...")

            process_voice_input()

        elif choice == '2':
            # Text mode
            clear_screen()
            print("=" * 50)
            print("📝 TEXT MODE - Type your message:")
            print("=" * 50)

            user_input = input("> ")

            if user_input.strip():
                process_text_input(user_input)

        elif choice == '3':
            # Exit
            print("\nExiting the application. Goodbye! 👋")
            break

        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    finally:
        # Clean up
        pygame.mixer.quit()

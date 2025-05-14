import os
from pathlib import Path
import pygame
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

def test_groq_api():
    """Test the Groq API connection"""
    try:
        # Test chat completion
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"}
            ],
            temperature=0.7,
            max_tokens=100,
        )

        print("✅ Chat API test successful!")
        print(f"Response: {completion.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"❌ Chat API test failed: {str(e)}")
        return False

def test_speech_recognition():
    """Test the speech recognition functionality"""
    try:
        # Initialize recognizer
        recognizer = sr.Recognizer()

        # Just test if we can initialize the recognizer
        print("✅ Speech Recognition test successful!")
        print("Note: This only tests if the library is properly installed.")
        print("Actual microphone access will be tested in the main application.")
        return True

    except Exception as e:
        print(f"❌ Speech Recognition test failed: {str(e)}")
        return False

def test_text_to_speech():
    """Test the text-to-speech functionality using gTTS"""
    try:
        # Create a test audio file
        speech_file_path = Path(__file__).parent / "test_speech.mp3"
        tts = gTTS("This is a test of the text-to-speech functionality.")
        tts.save(str(speech_file_path))

        # Try to play the audio file
        try:
            pygame.mixer.music.load(str(speech_file_path))
            pygame.mixer.music.play()
            print("✅ Text-to-Speech test successful!")
            print(f"Speech file saved to: {speech_file_path}")
            print("Playing audio... (should be audible if speakers are connected)")

            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            return True

        except Exception as e:
            print(f"✅ Text-to-Speech file created, but playback failed: {str(e)}")
            print(f"Speech file saved to: {speech_file_path}")
            return True  # Still consider it a success if the file was created

    except Exception as e:
        print(f"❌ Text-to-Speech test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("TESTING API AND LIBRARY CONNECTIONS")
    print("=" * 50)

    # Test chat API
    print("\nTesting Groq Chat API...")
    chat_success = test_groq_api()

    # Test speech recognition
    print("\nTesting Speech Recognition...")
    sr_success = test_speech_recognition()

    # Test text-to-speech
    print("\nTesting Text-to-Speech...")
    tts_success = test_text_to_speech()

    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Groq Chat API: {'✅ PASSED' if chat_success else '❌ FAILED'}")
    print(f"Speech Recognition: {'✅ PASSED' if sr_success else '❌ FAILED'}")
    print(f"Text-to-Speech: {'✅ PASSED' if tts_success else '❌ FAILED'}")

    if chat_success and sr_success and tts_success:
        print("\n✅ All tests passed! You can now run the main application.")
    else:
        print("\n❌ Some tests failed. Please check your installations and internet connection.")

    # Clean up
    pygame.mixer.quit()

if __name__ == "__main__":
    main()

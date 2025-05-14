# Voice-to-Voice AI Assistant

A voice-to-voice AI assistant application that allows users to interact with an AI through speech or text input and receive spoken responses. The application uses Groq's models for speech-to-text, text-to-speech, and chat functionality.

## Features

- **Voice Input**: Record your voice and have it transcribed to text
- **Text Input**: Type your message if you prefer not to speak
- **AI Response**: Get intelligent responses from Groq's LLM
- **Voice Output**: Hear the AI's response through text-to-speech
- **Conversation Memory**: The assistant remembers previous exchanges for context
- **Low Latency**: Optimized for quick response times

## Requirements

- Python 3.8+
- Groq API key
- Microphone for voice input
- Speakers for audio output

## Installation

1. Clone this repository or download the files
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project directory and add your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

## Usage

Run the application:
```
python test2.py
```

The application provides two modes of interaction:

### Voice Mode
- Press 'r' to start recording your voice
- Speak your message
- Press 'q' to stop recording
- The AI will process your speech, generate a response, and speak it back to you

### Text Mode
- Press 't' to enter text mode
- Type your message and press Enter
- The AI will generate a response and speak it back to you

To exit the application, press 'e'.

## How It Works

1. **Speech-to-Text**: Uses Groq's Whisper model to transcribe your voice
2. **Chat Model**: Uses Groq's LLama 3 70B model to generate intelligent responses
3. **Text-to-Speech**: Uses Groq's PlayAI TTS to convert the response to speech
4. **Audio Playback**: Automatically plays the AI's response

## Technical Implementation

- **Groq API**: For speech-to-text, text-to-speech, and chat functionality
- **PyAudio**: For recording audio from the microphone
- **Pygame**: For playing audio responses
- **Keyboard**: For detecting key presses to control the application

## Troubleshooting

- **Microphone Issues**: Make sure your microphone is properly connected and set as the default input device
- **API Key Issues**: Verify that your Groq API key is correctly set in the `.env` file
- **Audio Playback Issues**: Ensure your speakers are connected and the volume is turned up

## Future Enhancements

- **Multiple Languages**: Add support for additional languages
- **Voice Selection**: Allow users to choose different voices for the AI
- **Continuous Listening**: Implement a wake word to start recording automatically
- **GUI Interface**: Add a graphical user interface for easier interaction
- **Custom Commands**: Add support for specific commands like setting reminders or playing music

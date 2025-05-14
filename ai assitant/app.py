
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torchaudio
from TTS.api import TTS

# Load Text Generation Model
model_name = "TheBloke/dolphin-2.7-mixtral-8x7b-GGUF"
try:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")
    text_generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0)
except Exception as e:
    print(f"Error loading text generation model: {e}")
    exit()

# Load Speech Synthesis Model
voice_model = "hexgrad/Kokoro-82M"
try:
    tts = TTS(voice_model)
except Exception as e:
    print(f"Error loading speech synthesis model: {e}")
    exit()

def generate_response(user_input):
    """Generate a natural response based on user input."""
    try:
        response = text_generator(user_input, max_length=100, do_sample=True)[0]["generated_text"]
        return response
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm sorry, I couldn't process that."

def text_to_speech(text):
    """Convert AI-generated text to speech."""
    try:
        tts.tts_to_file(text=text, file_path="output.wav")
        print("Audio generated: output.wav")
        return "output.wav"
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None

def main():
    print("Welcome to the AI Romantic Assistant!")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        response = generate_response(user_input)
        print(f"AI: {response}")
        audio_file = text_to_speech(response)
        if audio_file:
            try:
                torchaudio.load(audio_file)
            except Exception as e:
                print(f"Error loading audio file: {e}")

if __name__ == "__main__":
    main()

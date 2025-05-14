import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit import IndicProcessor
import torchaudio

# Load the translation model
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

src_lang, tgt_lang = "eng_Latn", "hin_Deva"  # Example: English to Hindi
model_name = "ai4bharat/indictrans2-en-indic-1B"

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForSeq2SeqLM.from_pretrained(
    model_name, 
    trust_remote_code=True, 
    torch_dtype=torch.float16,  
    attn_implementation="flash_attention_2"
).to(DEVICE)

ip = IndicProcessor(inference=True)

# Function to translate text
def translate_text(text):
    batch = ip.preprocess_batch([text], src_lang=src_lang, tgt_lang=tgt_lang)
    inputs = tokenizer(batch, truncation=True, padding="longest", return_tensors="pt").to(DEVICE)
    
    with torch.no_grad():
        generated_tokens = model.generate(**inputs, max_length=256, num_beams=5)
    
    translated_text = tokenizer.batch_decode(generated_tokens.cpu().tolist(), skip_special_tokens=True)
    return ip.postprocess_batch(translated_text, lang=tgt_lang)[0]

# Example TTS using OpenAI's TTS (replace with your preferred TTS model)
import pyttsx3  # You can replace this with any advanced TTS model

def text_to_speech(text):
    try:
        engine = pyttsx3.init()
        # Try to set Hindi voice if available, otherwise use default
        voices = engine.getProperty('voices')
        hindi_voice = next((v for v in voices if "hindi" in v.name.lower()), voices[0])
        engine.setProperty('voice', hindi_voice.id)
        engine.setProperty('rate', 150)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Error: {str(e)}")

# Example chatbot interaction
while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() == "exit":
        break
    
    try:
        translated_response = translate_text(user_input)
        print(f"Chatbot ({tgt_lang}): {translated_response}")
        text_to_speech(translated_response)
    except Exception as e:
        print(f"Translation Error: {str(e)}")

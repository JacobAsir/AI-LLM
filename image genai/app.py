import streamlit as st
from together import Together
import requests
from io import BytesIO

# Streamlit App Title
st.title("AI Image Generation with FLUX Models")
st.write("Generate images using FLUX models via Together AI. Use Text-to-Image Generation to create stunning visuals.")

# Sidebar Description
st.sidebar.title("Text-to-Image Generation")
st.sidebar.write("""
You can provide a text prompt describing the image you want to generate.
The model interprets the prompt and creates a new image based on the description.

**For example:**
- **Prompt**: A serene lake surrounded by mountains during sunrise.
- **Output**: A generated image matching this description.
""")

# User Input: Together AI API Key
api_key = st.text_input("Enter your Together AI API Key:", type="password")
if not api_key:
    st.stop()

# Initialize Together AI Client
client = Together(api_key=api_key)

# Function to Generate Image
def generate_image(prompt, model="black-forest-labs/FLUX.1-schnell", steps=4):
    try:
        response = client.images.generate(
            prompt=prompt, model=model, steps=steps
        )
        return response.data[0].url
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None

# Function to Download Image
def download_image(image_url):
    response = requests.get(image_url)
    return BytesIO(response.content)

# Text-to-Image Generation
st.header("Text-to-Image Generation")
prompt = st.text_input("Enter a text prompt to generate an image:")
if st.button("Generate Image"):
    if prompt:
        st.info("Generating image...")
        image_url = generate_image(prompt)
        if image_url:
            st.image(image_url, caption="Generated Image", width=500)  # Restored fixed width
            # Add download button
            img_data = download_image(image_url)
            st.download_button(
                label="Download Image",
                data=img_data,
                file_name="generated_image.png",
                mime="image/png",
            )
    else:
        st.warning("Please enter a text prompt.")

# Footer
st.write("Powered by Together AI and FLUX Models")
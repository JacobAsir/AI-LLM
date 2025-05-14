import streamlit as st
from transformers import pipeline
import torch
from diffusers import DiffusionPipeline

import os
from dotenv import load_dotenv
load_dotenv()

os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

# Set page configuration and layout
st.set_page_config(
    page_title="Manga Story & Storyboard Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache the narrative generation model
@st.cache_resource(show_spinner=True)
def load_narrative_model():
    st.info("Loading narrative generation model (GPT-2)...")
    narrative_pipeline = pipeline("text-generation", model="gpt2")
    return narrative_pipeline

# Cache the image generation model (Stability AI's stable-diffusion-3.5-large)
@st.cache_resource(show_spinner=True)
def load_image_model():
    st.info("Loading image generation model (Stable Diffusion x1 base-1.0)...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    pipe = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )
    pipe = pipe.to(device)
    return pipe

def main():
    st.title("Manga Story & Storyboard Generator")
    st.markdown("**Create your manga storyline with dialogues and a visual storyboard illustration!**")
    
    # Sidebar for input configuration
    with st.sidebar:
        st.header("Input Details")
        manga_prompt = st.text_area(
            "Manga Prompt",
            "A thrilling clash between samurai warriors in feudal Japan with supernatural mysticism."
        )
        genre = st.selectbox(
            "Genre", 
            ["Action", "Romance", "Fantasy", "Mystery", "Sci-Fi", "Slice of Life"]
        )
        storyboard_desc = st.text_area(
            "Storyboard Image Description",
            "A samurai standing in a moonlit battlefield with mystical lights illuminating the scene."
        )
        st.markdown("---")
        st.info("Click the **Generate** button to create your manga narrative and storyboard illustration. The first run may take a few minutes to download the necessary models.")

    # Main area to trigger generation
    st.markdown("### Generate Your Manga Story and Visual Storyboard")
    if st.button("Generate"):
        with st.spinner("Loading models and generating outputs..."):
            # Load the narrative model and generate text
            narrative_pipeline = load_narrative_model()
            prompt_text = f"Genre: {genre}\nManga Prompt: {manga_prompt}\nManga Story and Dialogues:\n"
            try:
                narrative_output = narrative_pipeline(prompt_text, max_length=300, num_return_sequences=1)
                manga_story = narrative_output[0]["generated_text"]
            except Exception as e:
                st.error(f"Error generating manga narrative: {e}")
                manga_story = "Narrative generation failed."
            
            # Load the image model and generate storyboard illustration
            image_pipeline = load_image_model()
            try:
                img_output = image_pipeline(storyboard_desc, num_inference_steps=30)
                storyboard_image = img_output.images[0]
            except Exception as e:
                st.error(f"Error generating storyboard image: {e}")
                storyboard_image = None

        # Display the outputs in a side-by-side layout
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Generated Manga Narrative & Dialogues")
            st.text_area("Narrative", value=manga_story, height=400)
        with col2:
            st.subheader("Generated Storyboard Illustration")
            if storyboard_image is not None:
                st.image(storyboard_image, caption="Storyboard Illustration", use_column_width=True)
            else:
                st.write("No image available. Please try again.")
    else:
        st.info("Fill in the details in the sidebar and click **Generate** to begin.")

if __name__ == "__main__":
    main()
import streamlit as st
from langchain_groq import ChatGroq
from together import Together
from PIL import Image
import base64
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["TOGETHER_API_KEY"] = os.getenv("TOGETHER_API_KEY")

# Initialize models
llm = ChatGroq(
    model_name="mixtral-8x7b-32768",
    temperature=0,
    max_tokens=300
)
together_client = Together(api_key=os.environ["TOGETHER_API_KEY"])

# Functions for generating manga story and storyboard image
def generate_manga_story(prompt, genre):
    messages = [
        ("system", f"""You're a manga storytelling AI. Create a {genre} manga with:
        - 3-5 panels
        - Expressive character dialogues (e.g., *shouting*, *gasping*)
        - Action descriptions in [brackets]
        - Maintain manga pacing and page flow."""),
        ("human", prompt)
    ]
    response = llm.invoke(messages)
    return response.content

def generate_storyboard_image(description):
    """Generate manga-style image using Together's FLUX model"""
    try:
        # Crafting a manga-specific prompt
        prompt = (
            f"Manga-style illustration: {description}, "
            "monochrome, clean line art, dynamic pose, expressive facial features, "
            "sharp details, screentone shading, speech bubble with dialogue, "
            "high contrast, professional manga panel style."
        )
        
        # Generate the image
        response = together_client.images.generate(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell-Free",
            steps=4  # Ensure steps are within the valid range
        )
        
        # Use the URL field from the response
        image_url = response.data[0].url
        return image_url  # Return the URL for display
    except Exception as e:
        st.error(f"Image generation failed: {str(e)}")
        return None

# Streamlit UI
st.set_page_config(page_title="Manga Story & Storyboard Generator", layout="wide", initial_sidebar_state="expanded")

# Sidebar for input details
with st.sidebar:
    st.header("Input Details")
    manga_prompt = st.text_area("Manga Prompt", "A thrilling clash between samurai warriors in feudal Japan with supernatural mysticism.")
    genre = st.selectbox("Genre", ["Action", "Romance", "Fantasy", "Sci-Fi", "Horror"])
    storyboard_desc = st.text_area("Storyboard Image Description", "A samurai standing in a moonlit battlefield with mystical lights illuminating the scene.")

# Main content
st.title("Manga Story & Storyboard Generator")
st.subheader("Create your manga storyline with dialogues and a visual storyboard illustration!")
st.markdown("### Generate Your Manga Story and Visual Storyboard")

if st.button("Generate"):
    with st.spinner("Generating your manga..."):
        try:
            # Generate manga story
            manga_story = generate_manga_story(manga_prompt, genre)
            
            # Generate storyboard image
            storyboard_image = generate_storyboard_image(storyboard_desc)
            
            # Display results
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Generated Manga Story")
                st.text_area("Manga Story", value=manga_story, height=400, label_visibility="collapsed")
            with col2:
                st.subheader("Generated Storyboard Illustration")
                if storyboard_image:
                    st.image(storyboard_image, caption="Storyboard Illustration", use_container_width=True)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
else:
    st.info("Fill in the details in the sidebar and click Generate to begin.")
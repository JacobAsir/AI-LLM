import os
import tempfile
from io import BytesIO

import streamlit as st
import requests
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from together import Together

from fpdf import FPDF
import imageio
from PIL import Image

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


#### Helper Functions

def generate_manga_story(prompt, genre, style, panel_layout):
    """
    Generate a manga story based on the prompt, genre, art style, and panel layout.
    """
    full_prompt = (
        f"You're a manga storytelling AI. Create a {genre} manga in a {style} style with:\n"
        f"- 3-5 panels arranged in a {panel_layout} layout,\n"
        f"- Expressive character dialogues (e.g., *shouting*, *gasping*),\n"
        f"- Detailed action descriptions in [brackets], and\n"
        f"- A natural manga pacing and page flow.\n"
        f'Based on the following idea:\n"{prompt}"'
    )
    messages = [("system", full_prompt)]
    response = llm.invoke(messages)
    return response.content

def generate_storyboard_image(description, style):
    """
    Generate a manga-style image using Together's FLUX model.
    """
    try:
        prompt = (
            f"Manga-style illustration in {style} style: {description}, "
            "monochrome, clean line art, dynamic pose, expressive facial features, "
            "sharp details, screentone shading, speech bubble with dialogue, "
            "high contrast, professional manga panel style."
        )
        response = together_client.images.generate(
            prompt=prompt,
            model="black-forest-labs/FLUX.1-schnell-Free",
            steps=4
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        st.error(f"Image generation failed: {str(e)}")
        return None


def export_pdf(story_text, panel_images):
    """
    Export the manga story and panel images as a PDF document.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, story_text)

    for idx, img_url in enumerate(panel_images):
        try:
            response = requests.get(img_url)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(response.content)
                tmp_file.flush()
                image_path = tmp_file.name
            pdf.add_page()
            pdf.image(image_path, x=10, y=10, w=pdf.w - 20)
            os.remove(image_path)
        except Exception:
            continue
    pdf_data = pdf.output(dest='S').encode('latin1')
    return pdf_data


def generate_animated_gif(image_urls, duration=1):
    """
    Generate an animated GIF from a sequence of image URLs.
    """
    frames = []
    for url in image_urls:
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            frames.append(img)
        except Exception:
            continue
    if frames:
        gif_bytes = BytesIO()
        frames[0].save(
            gif_bytes,
            format='GIF',
            save_all=True,
            append_images=frames[1:],
            duration=duration * 1000,
            loop=0
        )
        gif_bytes.seek(0)
        return gif_bytes
    return None


#### Session State Initialization
if "manga_story" not in st.session_state:
    st.session_state.manga_story = None
if "prompt_image" not in st.session_state:
    st.session_state.prompt_image = None
if "storyboard_images" not in st.session_state:
    st.session_state.storyboard_images = []  # list of tuples (description, image_url)


#### Streamlit UI Configuration
st.set_page_config(page_title="MANGA-AI Enhanced", layout="wide")
st.title("MANGA-AI Enhanced: Create Your Own Manga Story & Visuals")


#### Sidebar: Input Details
with st.sidebar:
    st.header("Input Details")
    manga_prompt = st.text_area(
        "Manga Prompt",
        "Two high school students, Taki from Tokyo and Mitsuha from a rural town, mysteriously switch bodies. "
        "Communicating through messages, they develop feelings for each other. As they try to meet, "
        "a shocking truth unfolds, testing love, fate, and destiny."
    )
    genre = st.selectbox("Genre", ["Romance", "Action", "Fantasy", "Sci-Fi", "Horror"])
    style = st.selectbox("Manga Style", ["Shonen", "Shojo", "Seinen", "Kodomo", "Alternative"])
    panel_layout = st.radio("Panel Layout", ["Linear Sequence", "Grid", "Cinematic"])

    st.markdown("---")
    st.subheader("Storyboard Customization")
    storyboard_desc = st.text_area(
        "Storyboard Image Description", 
        "Dynamic showdown between rivals in an urban setting."
    )
    
    # Button to generate the manga story and main illustration
    if st.button("Generate Manga Story"):
        st.session_state.manga_story = generate_manga_story(manga_prompt, genre, style, panel_layout)
        st.session_state.prompt_image = generate_storyboard_image(manga_prompt, style)

    # Button to generate additional custom storyboard images
    if st.button("Generate Custom Storyboard Image"):
        if storyboard_desc.strip():
            image_url = generate_storyboard_image(storyboard_desc, style)
            if image_url:
                st.session_state.storyboard_images.append((storyboard_desc, image_url))
        else:
            st.warning("Please provide a description for the storyboard image.")


#### Main Content: Display Story and Visuals
st.subheader("Your Manga Creation")
if st.session_state.manga_story or st.session_state.prompt_image or st.session_state.storyboard_images:
    # Two columns: story text on the left, main illustration on the right
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Generated Manga Story")
        st.text_area("Manga Story", value=st.session_state.manga_story or "", height=400)
    with col2:
        st.markdown("### Main Manga Illustration")
        if st.session_state.prompt_image:
            st.image(st.session_state.prompt_image, caption="Main Manga Illustration", use_container_width=True)

    st.markdown("---")
    st.markdown("### Custom Storyboard Panels")
    if panel_layout == "Grid":
        # Display panels in a grid layout (2 per row)
        cols = st.columns(2)
        for idx, (desc, img_url) in enumerate(st.session_state.storyboard_images):
            with cols[idx % 2]:
                st.markdown(f"**Panel {idx + 1}: {desc}**")
                st.image(img_url, use_container_width=True)
    else:
        # Use an expander for each panel in linear or cinematic style
        for idx, (desc, img_url) in enumerate(st.session_state.storyboard_images, start=1):
            with st.expander(f"Panel {idx}: {desc}"):
                st.image(img_url, caption=f"Panel {idx}", use_container_width=True)


#### Additional Features

# Export Manga as PDF
if st.session_state.manga_story and (st.session_state.prompt_image or st.session_state.storyboard_images):
    if st.button("Download Manga as PDF"):
        pdf_images = []
        if st.session_state.prompt_image:
            pdf_images.append(st.session_state.prompt_image)
        for _, url in st.session_state.storyboard_images:
            pdf_images.append(url)
        pdf_data = export_pdf(st.session_state.manga_story, pdf_images)
        st.download_button("Download PDF", data=pdf_data, file_name="manga_story.pdf", mime="application/pdf")

# Animated GIF from Panel Images
all_images = []
if st.session_state.prompt_image:
    all_images.append(st.session_state.prompt_image)
for _, url in st.session_state.storyboard_images:
    all_images.append(url)
if all_images and st.button("Generate Animated GIF"):
    gif_bytes = generate_animated_gif(all_images, duration=1)
    if gif_bytes:
        st.image(gif_bytes, caption="Animated Manga Panels", use_container_width =True)
    else:
        st.warning("Could not generate the animated GIF. Please try again.")

# Gallery of Creations (Session Gallery)
if st.session_state.manga_story:
    with st.expander("Gallery of Creations"):
        st.info("This session's creations:")
        st.write("Manga Story:")
        st.write(st.session_state.manga_story)
        if st.session_state.prompt_image:
            st.image(st.session_state.prompt_image, caption="Main Illustration", use_container_width =True)
        for idx, (desc, img_url) in enumerate(st.session_state.storyboard_images, start=1):
            st.image(img_url, caption=f"Panel {idx}: {desc}", use_container_width =True)
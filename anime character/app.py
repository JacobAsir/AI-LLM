import streamlit as st
import os
from dotenv import load_dotenv
import streamlit.components.v1 as components

from langchain_groq import ChatGroq
from together import Together

# -----------------------------------------------------------------------------
# Environment & Model Initialization
# -----------------------------------------------------------------------------
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["TOGETHER_API_KEY"] = os.getenv("TOGETHER_API_KEY")

# Initialize the language model for generating character details (not displayed)
llm = ChatGroq(
    model_name="mixtral-8x7b-32768",  # Adjust as needed
    temperature=0,
    max_tokens=300
)

# Initialize the Together client (optional, if you plan to generate additional imagery)
together_client = Together(api_key=os.environ["TOGETHER_API_KEY"])

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def generate_character_details(name, traits, style, backstory):
    """
    Generate a detailed anime character description using ChatGroq.
    The description is generated in the background to inform future assets,
    but it will not be displayed.
    """
    prompt = (
        f"Generate a detailed and creative anime character description for an original character named {name}.\n"
        f"Traits: {traits}.\n"
        f"Preferred style: {style}.\n"
        f"Backstory: {backstory}.\n"
        "Focus on unique visual features suitable for a 3D representation."
    )
    messages = [
        ("system", "You are a creative anime character generator AI."),
        ("human", prompt)
    ]
    response = llm.invoke(messages)
    return response.content

def display_3d_model_viewer(model_url):
    """
    Embed a 360° interactive 3D model viewer using Google’s <model-viewer> component.
    The viewer is centered on the page.
    """
    html_code = f"""
    <html>
      <head>
        <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
        <style>
          body {{ margin: 0; }}
          .viewer-container {{
             display: flex;
             justify-content: center;
             align-items: center;
             width: 100%;
          }}
          model-viewer {{
             width: 80%;
             height: 500px;
          }}
        </style>
      </head>
      <body>
        <div class="viewer-container">
          <model-viewer src="{model_url}" camera-controls auto-rotate background-color="#70BCD1">
          </model-viewer>
        </div>
      </body>
    </html>
    """
    components.html(html_code, height=550)

# -----------------------------------------------------------------------------
# Main Application (Streamlit UI Only)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Anime/Manga Character Creator", layout="wide")
st.title("Anime/Manga Character Creator")
st.subheader("360° Interactive Character Model Viewer")

# Sidebar for input
with st.sidebar:
    st.header("Input Your Character Details")
    character_name = st.text_input("Character Name", "Hikaru")
    character_traits = st.text_area("Character Traits", "Spiky hair, confident, agile, with mysterious powers")
    character_style = st.selectbox("Style Preference", ["Ghibli", "Shonen Jump", "Seinen", "Modern Anime"])
    backstory = st.text_area("Backstory Inspiration", "Raised in a small town with extraordinary abilities and destined for greatness.")
    model_url_input = st.text_input("3D Model URL (GLB format)", "https://modelviewer.dev/shared-assets/models/Astronaut.glb")

# When the button is clicked, generate the character details in the background.
if st.button("Generate Character"):
    with st.spinner("Generating character..."):
        _ = generate_character_details(character_name, character_traits, character_style, backstory)
        st.success("Character generated successfully!")

# Display the interactive 360° 3D viewer centered on the page.
st.markdown("<h2 style='text-align: center;'>Your 360° Interactive 3D Character Model</h2>", unsafe_allow_html=True)
display_3d_model_viewer(model_url_input)
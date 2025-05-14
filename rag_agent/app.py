import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["ACTIVELOOP_TOKEN"] os.getenv("ACTIVELOOP_TOKEN")

import os
import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import whisper
import numpy as np
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores import DeepLake
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain import hub
import gtts
from io import BytesIO
import tempfile

# Initialize Streamlit page configuration
st.set_page_config(page_title="AI Physics Tutor", layout="wide")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def initialize_rag_system():
    """Initialize the RAG system components"""
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    
    # Connect to existing DeepLake dataset
    dataset_path = f"hub://jacobasir/Phyics_Ncert"
    db = DeepLake(dataset_path=dataset_path, embedding_function=embeddings)
    
    retriever = db.as_retriever()
    retriever.search_kwargs['distance_metric'] = 'cos'
    retriever.search_kwargs['k'] = 3
    
    return retriever

def create_agent(retriever):
    """Create the agent with tools"""
    def retrieve_n_docs_tool(query: str) -> str:
        docs = retriever.get_relevant_documents(query)
        texts = [doc.page_content for doc in docs]
        return "\n---------------\n".join(texts)

    tools = [
        Tool(
            name="Physics_search",
            func=retrieve_n_docs_tool,
            description="Useful for answering questions about physics concepts"
        )
    ]

    prompt = hub.pull("hwchase17/openai-functions-agent")
    llm = ChatOpenAI(model="gpt-4")
    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_buffer = []

    def recv(self, frame):
        audio_data = frame.to_ndarray() / 32768.0
        self.audio_buffer.extend(audio_data)
        return frame

    def get_audio_buffer(self):
        return np.array(self.audio_buffer, dtype=np.float32)

def text_to_speech(text):
    """Convert text to speech using gTTS"""
    tts = gtts.gTTS(text, lang='en')
    fp = BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

def main():
    st.title("🎓 AI Physics Tutor")
    st.markdown("---")

    # Initialize RAG system and agent
    retriever = initialize_rag_system()
    agent_executor = create_agent(retriever)

    # Create two columns for the interface
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Chat Interface")
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "audio" in message:
                    st.audio(message["audio"])

    with col2:
        st.subheader("Input Options")
        input_method = st.radio("Choose input method:", ["Text", "Voice"])

        if input_method == "Voice":
            # Initialize Whisper model
            model = whisper.load_model("base")

            # WebRTC audio streamer
            audio_processor = webrtc_streamer(
                key="real-time-audio",
                mode=WebRtcMode.SENDONLY,
                audio_processor_factory=AudioProcessor,
                media_stream_constraints={"audio": True, "video": False},
                async_processing=True,
            )

            if st.button("Process Voice Input"):
                if audio_processor and audio_processor.audio_processor:
                    audio_buffer = audio_processor.audio_processor.get_audio_buffer()
                    if len(audio_buffer) > 0:
                        # Process audio with Whisper
                        audio = whisper.pad_or_trim(audio_buffer)
                        mel = whisper.log_mel_spectrogram(audio).to(model.device)
                        result = model.transcribe(audio_buffer)
                        
                        # Display transcribed text
                        user_input = result["text"]
                        st.session_state.chat_history.append({"role": "user", "content": user_input})
                        
                        # Get agent response
                        response = agent_executor.invoke({"input": user_input})
                        response_text = response['output']
                        
                        # Convert response to speech
                        audio_bytes = text_to_speech(response_text)
                        
                        # Add response to chat history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response_text,
                            "audio": audio_bytes
                        })
                        st.experimental_rerun()

        else:  # Text input
            user_input = st.text_input("Type your question here:")
            if st.button("Send"):
                if user_input:
                    # Add user message to chat
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    
                    # Get agent response
                    response = agent_executor.invoke({"input": user_input})
                    response_text = response['output']
                    
                    # Convert response to speech
                    audio_bytes = text_to_speech(response_text)
                    
                    # Add response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response_text,
                        "audio": audio_bytes
                    })
                    st.experimental_rerun()

if __name__ == "__main__":
    main()
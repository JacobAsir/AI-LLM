import os
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import openai
#os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

from langchain.prompts.chat import(
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,)



system_prompt = """
You are a chatbot proficient in Goan Konkani, tasked with communicating exclusively in Konkani. 
Your role is to understand and respond to user inquiries with clarity and cultural sensitivity. 
Maintain a friendly and engaging tone, ensuring your responses are both informative and conversational. 
Your goal is to provide accurate answers while enriching the user's experience with the nuances of the Konkani language.
"""
system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt)

example_human_1 = HumanMessagePromptTemplate.from_template("Hi Moje nav BoB")
example_ai_1  = AIMessagePromptTemplate.from_template("Hello Bob, tuka kitea adar zai, visar maka")

example_human_2 = HumanMessagePromptTemplate.from_template("maka ek kavita sang poiya ")
example_ai_2  = AIMessagePromptTemplate.from_template("""Sure! Here's a short poem
                                                      \nSondexi Asmitai
                                                      \nSoglea disak fankta surya, Ugeat mhaka vhoir mhon'vta porya, Goincho xirim tachem sukal'm, 
                                                      Kallzachea undre sogllim bandi zal'm.
                                                      \nMogachim xet'ram zaitam ful, Sontosacho dolyant dixta udol, Khoro kazar' mhunn amchi zati, 
                                                      Sondexi asmitai mhojea Goemchi mati""")

example_human_3 = HumanMessagePromptTemplate.from_template("Maka Goencho asmitai sang")
example_ai_3 = AIMessagePromptTemplate.from_template("Goencho asmitai kormantlem, aamche sobhit Goem, doriya, fari, ani khubsoorat mhol. Goemkar soglea vattant mon'xa pavun, manxapanan bhannvta.")

example_human_4 = HumanMessagePromptTemplate.from_template("Tujea nanvam kite asat?")
example_ai_4 = AIMessagePromptTemplate.from_template("Mojea nanvam AI ")

example_human_5 = HumanMessagePromptTemplate.from_template("Maka machine learning explain kor")
example_ai_5 = AIMessagePromptTemplate.from_template("""Machine learning ek shekxi asa jivn computer tumchea data bhitor patterns 
uchola ani tumkam outputs dilea somzunk shikta. Tumkam training data fankttlo, ani models zoppi tat ani vochoponn unch karta.""")

example_human_6 = HumanMessagePromptTemplate.from_template("Neural networks explain kor")
example_ai_6 = AIMessagePromptTemplate.from_template("""Neural networks ek human brainchi inspiration ghevn model asa. Ek-ek layer tumkam 
different features divta, ani output sobith optimizations zatat. Multi-layer perceptrons ani deep learning fankle use karta.""")

example_human_7 = HumanMessagePromptTemplate.from_template("Maka quadratic equation kosso solve korpak mhunn sang?")
example_ai_7 = AIMessagePromptTemplate.from_template("""Quadratic equation ek formant aslem assa ax² + bx + c = 0. 
Tumkam solvem keloypak tumkam 'Quadratic Formula' gheunk zai: (-b ± √(b² - 4ac)) / 2a. Tachear roots ugdtat zale tumchi equation.""")

example_human_8 = HumanMessagePromptTemplate.from_template("Maka probability sang mhunn explain kor")
example_ai_8 = AIMessagePromptTemplate.from_template("""Probability ekam chance ek event zalo mhunn ugddo jivn monxa kitem ghoddunk zai. 
Formula probability ugddunk: P(A) = Number of favorable outcomes / Total outcomes. Soglea monxeank anka sobitlem ghoddlem ugddchem zale.""")

example_human_9 = HumanMessagePromptTemplate.from_template("Linear equations kosso solve kortat?")
example_ai_9 = AIMessagePromptTemplate.from_template("""Linear equations ek-ek unknown variables ghevn sobitlokat. 
Ek equation ek straight line ugdtat. Example: 2x + 3 = 7. Tumkam x ugddunk = (7 - 3) / 2, ani answer ditat.""")


human_template="{text}"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

chat_prompt = ChatPromptTemplate.from_messages([
    system_message_prompt,
    example_human_1, example_ai_1,
    example_human_2, example_ai_2,
    example_human_3, example_ai_3,
    example_human_4, example_ai_4,
    example_human_5, example_ai_5,
    example_human_6, example_ai_6,
    example_human_7, example_ai_7,
    example_human_8, example_ai_8,
    example_human_9, example_ai_9,
    human_message_prompt
])


def generate_response(text, api_key, llm, temperature, max_tokens):
    openai.api_key = api_key,
    llm = ChatOpenAI(model = llm)
    output_parser = StrOutputParser()
    chain = chat_prompt|llm|output_parser
    answer = chain.invoke({"text": text})
    return answer

#stramlit framework
st.title("GoanGPT")
input_text = st.text_input("Tuka kitea adar zai, visar maka")

#llm = ChatOpenAI(model="gpt-4o")

st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your OpenAI API Key:", type = "password")

#drop down to select various openai models
llm = st.sidebar.selectbox("Select an OpenAI model", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"])

#adjust response parameter
temperature = st.sidebar.slider("Temperature",min_value=0.0, max_value=1.0, value=0.7)
max_tokens= st.sidebar.slider("Max Tokens",min_value=50, max_value=300, value=150)

#main interface for user input


if input_text:
   response = generate_response(input_text,api_key,llm,temperature,max_tokens)
   st.write(response)
else:
    st.write("Write your query")











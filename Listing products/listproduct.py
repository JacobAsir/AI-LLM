import os
from dotenv import load_dotenv
load_dotenv()

os.environ["COHERE_API_KEY"] = os.getenv("COHERE_API_KEY")

from langchain_cohere import ChatCohere
import streamlit as st
from langchain.prompts.chat import(
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,)


llm = ChatCohere(model="command-r-plus-08-2024")



system_prompt = """
You are helpful assitant and your task is extract key attributes from the
description of the given product items 
"""
system_message_prompt = SystemMessagePromptTemplate.from_template(system_prompt)

example_human_1 = HumanMessagePromptTemplate.from_template("Zara Women's Blazer, Black Size: L Excellent condition, worn twice for meetings. Comes with original buttons and extra fabric patch. Purchased for 5,000 JPY.")
example_ai_1 = AIMessagePromptTemplate.from_template("""Extracted Attributes:
                                                        \nSize: L
                                                        \nColor: Black
                                                        \nOriginal retail price: 5,000 JPY
                                                        \n"tem condition: Excellent
                                                        \nWear frequency: Worn twice""")

example_human_2 = HumanMessagePromptTemplate.from_template("H&M Denim Jeans, Blue Size: 32 Barely used, no signs of wear. Perfect for casual outings")
example_ai_2 = AIMessagePromptTemplate.from_template("""Extracted Attributes:
                                                        \nSize: 32
                                                        \nColor: Blue
                                                        \nOriginal retail price: NONE
                                                        \nItem condition: Barely used
                                                        \nUsage: Casual outings""")


example_human_3 = HumanMessagePromptTemplate.from_template("Apple iPhone 13 Pro, 128GB Space Gray Barely used, includes original box and charger. Screen protector applied since day one. Originally bought for 1,000 JPY")
example_ai_3 = AIMessagePromptTemplate.from_template("""Extracted Attributes:
                                                        \nModel: iPhone 13 Pro
                                                        \nStorage: 128GB
                                                        \nColor: Space Gray
                                                        \nOriginal retail price: 1,000 JPY
                                                        \nItem condition: Barely used
                                                        \nAccessories: Original box and charger""")


example_human_4 = HumanMessagePromptTemplate.from_template("Sony WH-1000XM4 Headphones, Black Lightly used, in pristine condition. Comes with case and charging cable.")
example_ai_4 = AIMessagePromptTemplate.from_template( """Extracted Attributes:
                                                        \nModel: WH-1000XM4
                                                        \nColor: Black
                                                        \nOriginal retail price: NONE
                                                        \nItem condition: Lightly used
                                                        \nAccessories: Case and charging cable""")


example_human_5 = HumanMessagePromptTemplate.from_template("IKEA Billy Bookcase, White Mint condition, assembled but never used. Perfect for any living room or office.")
example_ai_5 = AIMessagePromptTemplate.from_template("""Extracted Attributes:
                                                        \nModel: Billy
                                                        \nColor: White
                                                        \nOriginal retail price: NONE
                                                        \nItem condition: Mint
                                                        \nUsage: Living room/office""")


example_human_6 = HumanMessagePromptTemplate.from_template("Dyson V11 Cordless Vacuum Cleaner Used gently for six months, works like new. Comes with all original attachments. Originally priced at 600 JPY")
example_ai_6 = AIMessagePromptTemplate.from_template("""Extracted Attributes:
                                                        \nModel: V11
                                                        \nOriginal retail price: 600 JPY
                                                        \nItem condition: Used gently
                                                        \nDuration of use: Six months
                                                        \nAccessories: All original attachments""")




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
    human_message_prompt
])

#stramlit framework

st.title("Extract Key Attributes")
input_text = st.text_input("user-generated listing description")

llm = ChatCohere(model="command-r-plus-08-2024")

if input_text:
    chain = chat_prompt | llm 
    response = chain.invoke({"text": input_text})

    st.write(response.content)
import os
from langchain_openai import ChatOpenAI  # Correct import for ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import HumanMessage

# Initialize the OpenAI GPT-4-128k model using your API key from environment
api_key = os.getenv("OPENAI_API_KEY")  # Make sure the API key is set
chat = ChatOpenAI(model="gpt-4-turbo", api_key=api_key)

# Load your large document
with open("large_outline.txt", "r") as file:
    large_text = file.read()

from langchain.text_splitter import RecursiveCharacterTextSplitter

# Use RecursiveCharacterTextSplitter instead of CharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=100)
chunks = splitter.split_text(large_text)

# Process each chunk with GPT-4-turbo using the invoke method
for chunk in chunks:
    response = chat.invoke([HumanMessage(content=chunk)])
    print(response.content)
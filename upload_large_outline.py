import os
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm  # For progress bar
import concurrent.futures  # For concurrency

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the OpenAI GPT-4-128k model using your API key from environment
api_key = os.getenv("OPENAI_API_KEY")  # Ensure the API key is set correctly
chat = ChatOpenAI(model="gpt-4-turbo", api_key=api_key)

# Load your large document
with open("large_outline.txt", "r") as file:
    large_text = file.read()

# Use RecursiveCharacterTextSplitter to split the text into manageable chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=100)
chunks = splitter.split_text(large_text)

# Define a function to process each chunk in a separate thread
def process_chunk(chunk):
    try:
        response = chat.invoke([HumanMessage(content=chunk)])
        return response.content
    except Exception as e:
        logger.error(f"Error processing chunk: {e}")
        return None  # Handle the error and return None if there's a failure

# Collect the processed results in order
results = [None] * len(chunks)  # Placeholder for results to maintain order

# Use ThreadPoolExecutor to process chunks concurrently
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Submit each chunk along with its index to the executor
    futures = {executor.submit(process_chunk, chunk): index for index, chunk in enumerate(chunks)}

    # Use tqdm to display progress as the chunks are processed
    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing Chunks"):
        index = futures[future]  # Get the index of the chunk
        result = future.result()
        if result:
            results[index] = result

# Filter out None results before writing to the file
filtered_results = [result for result in results if result is not None]

# Write the combined output to a file in the correct order
with open("analyzedFileOutput.html", "w") as output_file:
    output_file.write("\n".join(filtered_results))

logger.info("Processing complete. Output written to analyzedFileOutput.html")

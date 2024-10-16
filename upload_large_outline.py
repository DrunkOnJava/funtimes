import os
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
import concurrent.futures
from jinja2 import Environment, FileSystemLoader
from lxml import etree, html
import re  # Import regular expressions for manual minification


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the OpenAI GPT-4-128k model using your API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OpenAI API key is not set. Please set it as an environment variable.")
    exit(1)

chat = ChatOpenAI(model="gpt-4-turbo", api_key=api_key)

# Load your large document
try:
    with open("large_outline.txt", "r", encoding='utf-8') as file:
        large_text = file.read()
except FileNotFoundError:
    logger.error("The file 'large_outline.txt' was not found. Ensure the file exists.")
    exit(1)

# Use RecursiveCharacterTextSplitter to split the text into manageable chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=100)
chunks = splitter.split_text(large_text)

# Define a function to process each chunk
def process_chunk(chunk):
    try:
        response = chat.invoke([HumanMessage(content=chunk)])
        return response.content
    except Exception as e:
        logger.error(f"Error processing chunk: {e}")
        return None

# Process chunks concurrently
results = [None] * len(chunks)
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = {executor.submit(process_chunk, chunk): index for index, chunk in enumerate(chunks)}
    for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing Chunks"):
        index = futures[future]
        result = future.result()
        if result:
            results[index] = result

# Filter out None results
filtered_results = [result for result in results if result is not None]

# Set up Jinja2 environment and render template
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.html')
rendered_html = template.render(chunks=filtered_results)

# Validate the HTML
try:
    parser = html.HTMLParser()
    etree.fromstring(rendered_html, parser)
    logger.info("HTML validation successful. No syntax errors found.")
except etree.XMLSyntaxError as e:
    logger.error(f"HTML validation failed: {e}")

# Manual HTML Minification
def manual_minify(html_content):
    """ Manually minify the HTML content by removing extra spaces, newlines, and comments. """
    # Remove comments
    html_content = re.sub(r"<!--.*?-->", "", html_content, flags=re.DOTALL)
    
    # Remove unnecessary whitespace
    html_content = re.sub(r">\s+<", "><", html_content)  # Remove spaces between HTML tags
    html_content = re.sub(r"\s{2,}", " ", html_content)  # Replace multiple spaces with a single space
    
    return html_content

# Minify the HTML using the manual minification function
minified_html = manual_minify(rendered_html)

# Write minified HTML to file
try:
    with open("analyzedFileOutput.html", "w", encoding='utf-8') as output_file:
        output_file.write(minified_html)
    logger.info("Minified HTML output written to analyzedFileOutput.html")
except Exception as e:
    logger.error(f"Failed to write minified HTML to file: {e}")
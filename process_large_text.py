#!/usr/bin/env python3

import os
import argparse
import pathlib
import logging
import concurrent.futures
from tqdm import tqdm
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import HumanMessage, SystemMessage
from lxml import html
import htmlmin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process a large text file with GPT-4.')
    parser.add_argument('--input_file', type=str, default='/Users/griffin/my_openai_project/large_outline.txt', help='Path to the input text file.')
    parser.add_argument('--output_file', type=str, default='/Users/griffin/my_openai_project/analyzedFileOutput.html', help='Path to the output HTML file.')
    parser.add_argument('--chunk_size', type=int, default=2048, help='Chunk size for text splitting.')
    parser.add_argument('--chunk_overlap', type=int, default=100, help='Chunk overlap for text splitting.')
    args = parser.parse_args()

    input_file_path = args.input_file
    output_file_path = args.output_file
    chunk_size = args.chunk_size
    chunk_overlap = args.chunk_overlap

    # Retrieve API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    # Load your large document
    with open(input_file_path, "r", encoding="utf-8") as file:
        large_text = file.read()

    # Use RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(large_text)

    logger.info('Total chunks to process: %d', len(chunks))

    # Prepare the output directory
    output_dir = pathlib.Path(output_file_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Define the processing function
    def process_chunk(chunk):
        # Initialize a new ChatOpenAI instance within each thread
        chat = ChatOpenAI(
            model="gpt-4-turbo",
            api_key=api_key,
            temperature=0.7,
            max_tokens=2000  # Adjusted for the task and model limits
        )
        system_message = SystemMessage(content=(
            "You are an assistant that analyzes the given text to determine a better way "
            "to format it in HTML, CSS, and JavaScript. Please also provide additional context "
            "or content where appropriate."
        ))
        human_message = HumanMessage(content=chunk)
        try:
            response = chat.invoke([system_message, human_message])
            return response.content
        except Exception as e:
            logger.error('Error processing chunk: %s', e)
            return ''

    # Process the chunks concurrently
    responses = []

    logger.info('Starting processing of the text file.')

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all tasks
        futures = {executor.submit(process_chunk, chunk): idx for idx, chunk in enumerate(chunks)}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing Chunks"):
            idx = futures[future]
            try:
                result = future.result()
                responses.append(result)
                logger.debug('Processed chunk %d', idx)
            except Exception as e:
                logger.error('Error processing chunk %d: %s', idx, e)
                responses.append('')

    logger.info('Finished processing all chunks.')

    # Combine the responses into a single string
    combined_content = '\n'.join(responses)

    # Validate the output HTML
    try:
        # Attempt to parse the HTML content
        parsed_html = html.fromstring(combined_content)
        logger.info('HTML output is valid.')
    except Exception as e:
        logger.error('HTML validation error: %s', e)
        # Optionally, handle the error or raise an exception

    # Post-process the HTML (minify)
    minified_html = htmlmin.minify(combined_content, remove_empty_space=True)

    # Write the minified HTML to the output file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(minified_html)

    logger.info('Minified HTML has been written to %s', output_file_path)

if __name__ == '__main__':
    main()

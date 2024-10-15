    return chunks

def display_large_output_simulation(output, chunk_size=1000):
    """
    Display large output in smaller chunks for testing without interactive input.
    """
    chunks = [output[i:i+chunk_size] for i in range(0, len(output), chunk_size)]
    for idx, chunk in enumerate(chunks, start=1):
        console.print(f"[yellow]Chunk {idx}/{len(chunks)}:[/yellow]\n{chunk}")
        # Simulate pressing Enter to continue for all chunks

# Test function with long input and long output handling
def test_large_input_output_handling_simulation():
    # Example large input (repeated sentence)
    large_input = "Explain quantum mechanics in detail." * 1000
    chunks = chunk_text(large_input)
    console.print(f"Total chunks created from input: {len(chunks)}")

    # Example large output (model's response)
    large_output = "Quantum mechanics is a fundamental theory in physics." * 500
    display_large_output_simulation(large_output)

# Modify the chat function to handle large inputs/outputs without requiring user input
def chat_with_large_input_handling_simulation(user_input):
    input_chunks = chunk_text(user_input)
    for chunk in input_chunks:  # Process each chunk
        response = "Simulated response for chunk"  # Simulating a response
        console.print(response)

# Simulating the integration
def main_simulation():
    console.print("\n[bold cyan]Testing Large Input/Output Handling[/bold cyan]")

    # Test with large input/output
    test_large_input_output_handling_simulation()

    # Example chat interaction with large input/output handling
    user_input = "Explain quantum mechanics in detail." * 1000
    chat_with_large_input_handling_simulation(user_input)

#!/usr/bin/env python3

import os
import json
from openai import OpenAI

client = OpenAI(api_key=load_api_key(openai_api_key_path))  # Import openai at the top
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.progress import Progress
from time import sleep

# Initialize the console for rich text output
console = Console()

# Constants
CONFIG_FILE = os.path.expanduser("~/.advanced_cli_tool_config.json")
HISTORY_FILE = os.path.expanduser("~/.advanced_cli_tool_history")
AVAILABLE_MODELS = [
    "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo",
    "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
]
SUPPORTED_FORMATS = ['.txt', '.pdf', '.py']  # Add .py to the list of supported formats

# Load API key from file
def load_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Set the OpenAI API key
openai_api_key_path = "/Users/griffin/my_openai_project/openAI_Terminal_MacOS2.txt"

# Progress indicator for large operations
def display_loading_bar(task_description, total_steps, step_duration=0.01):
    """
    Displays a loading bar for simulating long operations with a faster step duration for testing.
    """
    with Progress() as progress:
        task = progress.add_task(f"[cyan]{task_description}...", total=total_steps)

        while not progress.finished:
            sleep(step_duration)
            progress.update(task, advance=1)

def simulate_processing_large_input():
    # Simulate processing time
    sleep(1)

def simulate_loading_large_file(file_path):
    # Simulate loading time
    sleep(2)

def simulate_api_request():
    # Simulate API request time
    sleep(1)

def process_large_input_with_progress(user_input):
    input_chunks = [user_input[i:i+100] for i in range(0, len(user_input), 100)]
    for idx, chunk in enumerate(input_chunks, start=1):
        console.print(f"\n[cyan]Processing chunk {idx}/{len(input_chunks)}[/cyan]")
        simulate_processing_large_input()
        response = "Simulated response for chunk"  # Simulated response
        console.print(response)  # Assuming you want to print the response

def analyze_file_with_loading_bar(file_path):
    simulate_loading_large_file(file_path)
    console.print(f"[green]Finished analyzing {file_path}.")

def chat_with_loading_bars(user_input):
    console.print("[yellow]Starting chat session...[/yellow]")
    display_loading_bar("Processing input", total_steps=10, step_duration=0.1)

    response = get_model_response(user_input)
    console.print(f"[green]Model response:[/green] {response}")

def get_model_response(user_input):
    try:
        response = client.chat.completions.create(model="gpt-4-turbo",  # Use the appropriate model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ],
        max_tokens=150)
        return response.choices[0].message.content
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return "An error occurred while fetching the response."

def main_with_loading_bars():
    console.print("\n[bold cyan]Testing Progress Indicators and Loading Bars[/bold cyan]")

    # Example: Simulating loading a large file
    analyze_file_with_loading_bar("large_document.txt")

    # Example: Simulating a chat session with loading bars
    chat_with_loading_bars("This is a test input for the chat session.")

    # Return to main menu after tests
    main_menu()

def analyze_file(file_path):
    _, ext = os.path.splitext(file_path)
    if ext not in SUPPORTED_FORMATS:
        console.print(f"[red]Unsupported file format: {ext}[/red]")
        return
    if ext == '.py':
        analyze_python_file(file_path)
    else:
        console.print(f"Analyzing {ext} file content:")
        with open(file_path, 'r') as file:
            content = file.read()
            console.print(content)


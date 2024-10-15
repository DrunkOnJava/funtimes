def analyze_python_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
        console.print("Analyzing Python file content:")
        console.print(content)

def main_menu():
    session = PromptSession(
        history=FileHistory(HISTORY_FILE),
        auto_suggest=AutoSuggestFromHistory()
    )

    session = PromptSession(
        history=FileHistory(HISTORY_FILE),
        auto_suggest=AutoSuggestFromHistory()
    )

    while True:
        try:
            command = session.prompt("Enter a command: ", completer=WordCompleter([
                'help', 'analyze', 'chat', 'save', 'load', 'branch', 'summary', 'export_txt', 'export_pdf', 'switch_model', 'exit', 'test'
            ]))

            if command == 'help':
                console.print("Available Commands:")
                console.print("help: Show this help message")
                console.print("analyze: Analyze a file")
                console.print("chat: Start a chat session")
                console.print("save: Save the current conversation")
                console.print("load: Load a saved conversation")
                console.print("branch: Branch the current conversation")
                console.print("summary: Summarize the current conversation")
                console.print("export_txt: Export conversation to a TXT file")
                console.print("export_pdf: Export conversation to a PDF file")
                console.print("switch_model: Switch the active model")
                console.print("test: Run tests with loading bars")
                console.print("exit: Exit the CLI tool")
            elif command == 'analyze':
                file_path = session.prompt("Enter the path to the file you wish to analyze: ")
                analyze_file(file_path)
            elif command == 'chat':
                user_input = session.prompt("Enter your message: ")
                chat_with_loading_bars(user_input)
            elif command == 'test':
                main_with_loading_bars()
            elif command == 'exit':
                break
            else:
                console.print("[red]Unknown command. Type 'help' for a list of commands.[/red]")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main_menu()

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

def chat_with_loading_bars():
    console.print("[yellow]Starting chat session... Type 'exit' to end the chat.[/yellow]")
    session = PromptSession(history=FileHistory(HISTORY_FILE), auto_suggest=AutoSuggestFromHistory())

    while True:
        user_input = session.prompt("You: ")
        if user_input.lower() == "exit":
            console.print("[yellow]Ending chat session...[/yellow]")
            break

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


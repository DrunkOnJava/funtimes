#!/usr/bin/env python3

import os
import json
import logging
import requests
import atexit
import pickle
import argparse
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from docx import Document
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import yaml
import csv
import openai
from rich.console import Console
from fpdf import FPDF

# Global Constants
CONFIG_FILE = os.path.expanduser("~/.advanced_cli_tool_config.json")
AVAILABLE_MODELS = [
    "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo",
    "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
]
SUPPORTED_FORMATS = ['.txt', '.pdf', '.py']

# Global Variables
console = Console()
HISTORY_FILE = "command_history.txt"

class Config:
    def __init__(self, config_file=None, profile=None):
        self.config_file = config_file or CONFIG_FILE
        self.profile = profile or "default"
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                return json.load(file)
        return {}

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as file:
            json.dump(self.config, file, indent=2)

class ModelManager:
    def __init__(self, config):
        self.config = config

    def switch_model(self, model_name):
        if model_name in AVAILABLE_MODELS:
            self.config.set('default_model', model_name)
            console.print(f"[bold green]Switched to model: {model_name}[/bold green]")
        else:
            console.print(f"[red]Error: Model {model_name} is not available.[/red]")

class FileHandler:
    def __init__(self):
        self.supported_formats = {
            '.txt': self.read_text,
            '.pdf': self.read_pdf,
            '.docx': self.read_docx,
            '.png': self.read_image,
            '.jpg': self.read_image,
            '.jpeg': self.read_image,
            '.py': self.read_python,
            '.md': self.read_text,
            '.html': self.read_text,
            '.json': self.read_json,
            '.csv': self.read_csv,
            '.yaml': self.read_yaml,
            '.yml': self.read_yaml
        }

    def read_file(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() in self.supported_formats:
            return self.supported_formats[file_extension.lower()](file_path)
        raise ValueError(f"Unsupported file format: {file_extension}")

    def read_text(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()

    def read_pdf(self, file_path):
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            return ' '.join([page.extract_text() for page in reader.pages])

    def read_docx(self, file_path):
        doc = Document(file_path)
        return ' '.join([paragraph.text for paragraph in doc.paragraphs])

    def read_image(self, file_path):
        image = Image.open(file_path)
        return pytesseract.image_to_string(image)

    def read_python(self, file_path):
        with open(file_path, 'r') as file:
            return file.read()

    def read_json(self, file_path):
        with open(file_path, 'r') as file:
            return json.dumps(json.load(file), indent=2)

    def read_csv(self, file_path):
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            return "\n".join([",".join(row) for row in reader])

    def read_yaml(self, file_path):
        with open(file_path, 'r') as file:
            return yaml.dump(yaml.safe_load(file), default_flow_style=False)

class ChatManager:
    def __init__(self, config):
        self.config = config
        self.conversation = []

    def add_message(self, role, content):
        self.conversation.append({"role": role, "content": content})

    def get_conversation(self):
        return self.conversation

    def save_conversation(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.conversation, file, indent=2)
        console.print(f"[bold green]Conversation saved to {filename} successfully.[/bold green]")

    def load_conversation(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                self.conversation = json.load(file)
            console.print(f"[bold green]Conversation loaded from {filename} successfully.[/bold green]")
        else:
            console.print(f"[red]Error: File {filename} does not exist.[/red]")

    def branch_conversation(self):
        console.print("[cyan]Branching conversation...[/cyan]")
        console.print("[cyan]Branching logic not yet implemented.[/cyan]")

    def summarize_conversation(self):
        console.print("[cyan]Summarizing conversation...[/cyan]")

    def chat(self):
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == 'exit':
                break
            self.add_message("user", user_input)
            console.print("[yellow]Thinking...[/yellow]")
            response = self.generate_response(user_input)
            console.print(f"Assistant: {response}")
            self.add_message("assistant", response)

    def generate_response(self, user_input):
        model = self.config.get('default_model')
        if model.startswith("gpt"):
            return self.call_openai_api(user_input)
        elif model.startswith("claude"):
            return self.call_claude_api(user_input)
        return "[red]Error: Unsupported model[/red]"

    def call_openai_api(self, user_input):
        api_key = self.config.get('openai_key')
        if not api_key:
            return "[red]Error: OpenAI API key missing![/red]"
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {
            "model": self.config.get('default_model'),
            "messages": [{"role": "user", "content": user_input}],
            "max_tokens": 100,
            "temperature": 0.7
        }
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"[red]Error occurred: {e}[/red]"

    def call_claude_api(self, user_input):
        api_key = self.config.get('claude_key')
        if not api_key:
            return "[red]Error: Claude API key missing![/red]"
        headers = {"x-api-key": api_key}
        data = {
            "model": self.config.get('default_model'),
            "prompt": user_input,
            "max_tokens": 100,
            "temperature": 0.7
        }
        try:
            response = requests.post("https://api.anthropic.com/v1/completions", headers=headers, json=data)
            response.raise_for_status()
            return response.json()['completion']
        except Exception as e:
            return f"[red]Error occurred: {e}[/red]"

class HelpSystem:
    def __init__(self):
        self.commands = {
            'help': 'Show this help message',
            'analyze': 'Analyze a file',
            'chat': 'Start a chat session',
            'save': 'Save the current conversation',
            'load': 'Load a saved conversation',
            'branch': 'Branch the current conversation',
            'summary': 'Summarize the current conversation',
            'export_txt': 'Export conversation to a TXT file',
            'export_pdf': 'Export conversation to a PDF file',
            'switch_model': 'Switch the active model'
        }

    def get_help(self):
        help_message = "[bold cyan]Available Commands:[/bold cyan]\n"
        for command, description in self.commands.items():
            help_message += f"[bold yellow]{command}[/bold yellow]: {description}\n"
        return help_message

def export_conversation_to_pdf(conversation, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for message in conversation:
        pdf.multi_cell(0, 10, f"{message['role']}: {message['content']}")
    pdf.output(filename)
    console.print(f"[bold green]Conversation exported to {filename} successfully.[/bold green]")

def export_conversation_to_txt(conversation, filename):
    with open(filename, 'w') as file:
        for message in conversation:
            file.write(f"{message['role']}: {message['content']}\n")
    console.print(f"[bold green]Conversation exported to {filename} successfully.[/bold green]")

def save_state(conversation_manager):
    with open('tool_state.pkl', 'wb') as file:
        pickle.dump(conversation_manager, file)
    console.print("[bold green]State saved successfully.[/bold green]")

def load_state():
    if os.path.exists('tool_state.pkl'):
        with open('tool_state.pkl', 'rb') as file:
            return pickle.load(file)
    console.print("[bold yellow]No previous state found.[/bold yellow]")
    return None

def main():
    parser = setup_argparse()
    args = parser.parse_args()

    setup_logging(args.verbose)

    config = Config(config_file=args.config, profile=args.profile)
    conversation_manager = ChatManager(config)
    command_history = FileHistory(HISTORY_FILE)
    model_manager = ModelManager(config)
    file_handler = FileHandler()
    help_system = HelpSystem()

    session = PromptSession(
        history=command_history,
        auto_suggest=AutoSuggestFromHistory(),
        completer=WordCompleter(list(help_system.commands.keys()), ignore_case=True)
    )

    console.print("\n[bold cyan]Welcome to the Advanced OpenAI/Claude CLI Tool![/bold cyan]")
    console.print(f"[bold yellow]Current model: {config.get('default_model')}[/bold yellow]")
    console.print("[green]Type 'help' for a list of commands.[/green]")

    atexit.register(lambda: save_state(conversation_manager))

    command_actions = {
        'help': lambda: console.print(help_system.get_help()),
        'analyze': lambda: analyze_file(file_handler),
        'chat': lambda: conversation_manager.chat(),
        'save': lambda: save_conversation(conversation_manager),
        'load': lambda: load_conversation(conversation_manager),
        'branch': lambda: conversation_manager.branch_conversation(),
        'summary': lambda: console.print(conversation_manager.summarize_conversation()),
        'export_txt': lambda: export_conversation(conversation_manager, 'txt'),
        'export_pdf': lambda: export_conversation(conversation_manager, 'pdf'),
        'switch_model': lambda: switch_model(model_manager)
    }

    while True:
        try:
            user_input = session.prompt("Enter a command: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            break

        if user_input == 'exit':
            break
        elif user_input in command_actions:
            command_actions[user_input]()
        else:
            console.print(f"[red]Unknown command: {user_input}. Type 'help' for available commands.[/red]")

    console.print("[bold cyan]Thank you for using the Advanced OpenAI/Claude CLI Tool. Goodbye![/bold cyan]")

def analyze_file(file_handler):
    file_path = input("Enter the path to the file you wish to analyze: ")
    try:
        file_content = file_handler.read_file(file_path)
        console.print(f"[green]File content:[/green]\n{file_content}")
    except ValueError as e:
        console.print(f"[red]{e}[/red]")

def save_conversation(conversation_manager):
    filename = input("Enter filename to save conversation: ")
    conversation_manager.save_conversation(filename)

def load_conversation(conversation_manager):
    filename = input("Enter filename to load conversation: ")
    conversation_manager.load_conversation(filename)

def export_conversation(conversation_manager, file_type):
    filename = input(f"Enter filename to export conversation as {file_type.upper()}: ")
    if file_type == 'txt':
        export_conversation_to_txt(conversation_manager.get_conversation(), filename)
    elif file_type == 'pdf':
        export_conversation_to_pdf(conversation_manager.get_conversation(), filename)

def switch_model(model_manager):
    model_name = input("Enter model name to switch to: ")
    model_manager.switch_model(model_name)

def setup_argparse():
    parser = argparse.ArgumentParser(description="Advanced OpenAI/Claude CLI Tool")
    parser.add_argument('--config', type=str, help='Path to custom config file')
    parser.add_argument('--profile', type=str, help='User profile name')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    return parser

def setup_logging(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(filename='advanced_cli_tool.log', level=level, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    main()

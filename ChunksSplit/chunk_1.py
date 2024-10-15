
import os
import json
import logging
import requests
import argparse
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from prompt_toolkit.shortcuts import input_dialog
from openai import OpenAI

def load_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Load the API key from the file
api_key = load_api_key("/Users/griffin/my_openai_project/openAI_Terminal_MacOS2.txt")

client = OpenAI(api_key=api_key)

# Load the API key from the file
api_key = load_api_key("/Users/griffin/my_openai_project/openAI_Terminal_MacOS2.txt")

# Set the API key for the openai module

# Create a chat completion
response = client.chat.completions.create(model="gpt-4-turbo",
messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello! How can you assist me today?"}
])

# Print the response
print(response.choices[0].message.content)

def load_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Load the API key from the file
api_key = load_api_key("/Users/griffin/my_openai_project/openAI_Terminal_MacOS2.txt")

# Set the API key for the openai module

# Create a chat completion
response = client.chat.completions.create(model="gpt-4-turbo",
messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello! How can you assist me today?"}
])

# Print the response
print(response.choices[0].message.content)

# Global Constants
CONFIG_FILE = os.path.expanduser("~/.advanced_cli_tool_config.json")
HISTORY_FILE = "command_history.txt"
AVAILABLE_MODELS = [
    "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo",
    "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
]
SUPPORTED_FORMATS = ['.txt', '.pdf', '.docx', '.py', '.yaml', '.yml', '.json', '.csv']
# Global Variables
console = Console()

def load_api_key(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Load the API key from the file
api_key = load_api_key("/Users/griffin/my_openai_project/openAI_Terminal_MacOS2.txt")

# Set the API key for the openai module

# Create a chat completion
response = client.chat.completions.create(model="gpt-4-turbo",
messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello! How can you assist me today?"}
])

# Print the response
print(response.choices[0].message.content)
console = Console()

# Verbose Logging Setup
def setup_logging(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(filename='advanced_cli_tool.log', level=level, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    if verbose:
        console.print("[green]Verbose mode enabled. Detailed logs are being written.[/green]")

# Error Handling for Missing Config File
class Config:
    def __init__(self, config_file=None, profile=None):
        self.config_file = config_file or CONFIG_FILE
        self.profile = profile or "default"
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as file:
                    return json.load(file)
            except (json.JSONDecodeError, OSError) as e:
                console.print(f"[red]Error loading configuration file: {e}[/red]")
                return {}
        else:
            console.print("[red]Configuration file not found. Creating a new one...[/red]")
            self.save_config()  # Create a default config if file is missing
            return {}

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

    def save_config(self):
        try:
            with open(self.config_file, 'w') as file:
                json.dump(self.config, file, indent=2)
            console.print("[green]Configuration saved.[/green]")
        except OSError as e:
            console.print(f"[red]Error saving configuration file: {e}[/red]")

    def validate_config(self):
        # Ensure critical fields (e.g., API keys) exist
        if not self.get('openai_key') or not self.get('default_model'):
            console.print("[red]Error: Missing required configuration fields. Please update the configuration file.[/red]")
            return False
        return True

# Command Validation
def validate_command(command):
    if not command:
        console.print("[red]Error: No command provided.[/red]")
        return False
    if not isinstance(command, str):
        console.print("[red]Error: Command must be a string.[/red]")
        return False
    return True

# Retry Mechanism for API Calls
def api_call_with_retry(url, headers, data, retries=3, delay=2):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            console.print(f"[red]API request failed: {e} (Attempt {attempt + 1}/{retries})[/red]")
            time.sleep(delay)
            attempt += 1
    console.print("[red]All retries failed. Please check your network or API configuration.[/red]")
    return None


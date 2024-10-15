#!/usr/bin/env python3
import os
import sys
import subprocess
import mimetypes
from pathlib import Path

def install_dependencies():
    """Install required packages if they're missing."""
    required_packages = [
        "requests", "colorama", "openai", "InquirerPy", "prompt_toolkit",
        "tqdm", "halo", "cryptography"
    ]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing missing dependency: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install dependencies before importing
install_dependencies()

# Now we can safely import the rest
import configparser
from InquirerPy import inquirer
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from colorama import Fore, Style, init
from tqdm import tqdm
from halo import Halo
import requests
from cryptography.fernet import Fernet

# Initialize colorama
init(autoreset=True)

# Configuration management
config_file = Path.home() / ".openai_claude_config.ini"
config = configparser.ConfigParser()

def load_config():
    """Load or create configuration file."""
    if not config_file.exists():
        config['DEFAULT'] = {'Model': 'gpt-4-turbo', 'MaxTokens': '2048', 'Temperature': '0.7'}
        config['API'] = {'APIKey': ''}
        save_config('DEFAULT', 'Model', 'gpt-4-turbo')
    else:
        try:
            config.read(config_file)
        except configparser.Error as e:
            print(Fore.RED + f"Error reading configuration file: {e}")
            sys.exit(1)

def save_config(section, key, value):
    """Save a value to the configuration file."""
    if section not in config:
        config[section] = {}
    config[section][key] = value
    try:
        with open(config_file, 'w') as conf_file:
            config.write(conf_file)
    except IOError as e:
        print(Fore.RED + f"Error writing to configuration file: {e}")

# Encryption for API keys
def get_or_create_key():
    """Get or create encryption key for API key storage."""
    key_file = Path.home() / ".openai_claude_key"
    if not key_file.exists():
        key = Fernet.generate_key()
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
        except IOError as e:
            print(Fore.RED + f"Error writing encryption key: {e}")
            sys.exit(1)
    else:
        try:
            with open(key_file, 'rb') as f:
                key = f.read()
        except IOError as e:
            print(Fore.RED + f"Error reading encryption key: {e}")
            sys.exit(1)
    return key

cipher_suite = Fernet(get_or_create_key())

def encrypt_api_key(api_key):
    """Encrypt the API key."""
    return cipher_suite.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_key):
    """Decrypt the API key."""
    try:
        return cipher_suite.decrypt(encrypted_key.encode()).decode()
    except:
        print(Fore.RED + "Error decrypting API key. It may be invalid or corrupted.")
        return None

def generate_output(messages, model=None, max_tokens=None, temperature=None):
    """Generate output using the OpenAI API."""
    if model is None:
        model = config['DEFAULT']['Model']
    if max_tokens is None:
        max_tokens = int(config['DEFAULT']['MaxTokens'])
    if temperature is None:
        temperature = float(config['DEFAULT']['Temperature'])
    
    api_key = decrypt_api_key(config['API']['APIKey'])
    if not api_key:
        print(Fore.RED + "API key is missing or invalid. Please set a valid API key.")
        return None
    
    headers = {'Authorization': f'Bearer {api_key}'}
    data = {
        'model': model,
        'messages': messages,
        'max_tokens': max_tokens,
        'temperature': temperature
    }
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Error calling OpenAI API: {e}")
        return None

def upload_file():
    """Upload and read a file."""
    file_path = input("Enter the path to the file you wish to upload: ")
    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type.startswith('text/'):
            with open(file_path, 'r') as file:
                file_content = file.read()
            print(Fore.GREEN + f"Successfully read file: {file_path}")
            return file_content
        else:
            print(Fore.YELLOW + f"File type {mime_type} is not supported. Please upload a text file.")
            return None
    except Exception as e:
        print(Fore.RED + f"Failed to open file: {e}")
        return None

def set_api_key():
    """Set the API key."""
    api_key = prompt("Please enter your new API key: ", is_password=True).strip()
    if api_key:
        encrypted_key = encrypt_api_key(api_key)
        save_config('API', 'APIKey', encrypted_key)
        print(Fore.GREEN + "API key updated successfully.")
    else:
        print(Fore.YELLOW + "API key update cancelled.")

def select_model():
    """Select an AI model."""
    models = [
        "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo",
        "davinci", "curie", "babbage", "ada"
    ]
    model = inquirer.select(
        message="Select the model you want to use:",
        choices=models
    ).execute()
    save_config('DEFAULT', 'Model', model)
    print(Fore.GREEN + f"Model changed to {model}")
    return model

def get_user_input():
    """Get user input with command completion."""
    commands_completer = WordCompleter([
        'upload', 'help', 'exit', 'model', 'clear', 'set api key', 'change model',
        'set max tokens', 'set temperature'
    ], ignore_case=True)
    while True:
        user_input = prompt("You: ", completer=commands_completer).strip()
        if user_input:
            return user_input
        print(Fore.YELLOW + "Please enter a command or message.")

def help_menu():
    """Display the help menu."""
    print(Fore.GREEN + "Help Menu:")
    print("  upload - Upload a file for analysis")
    print("  exit - Exit the application")
    print("  model [model_name] - Change the AI model")
    print("  clear - Clear the screen")
    print("  set api key - Set the API key")
    print("  change model - Change the model used")
    print("  set max tokens [value] - Set the maximum number of tokens")
    print("  set temperature [value] - Set the temperature for responses")
    print("  help - Display this help menu")

def clear_screen():
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def process_command(command):
    """Process user commands."""
    if command == 'upload':
        content = upload_file()
        if content:
            print("File content loaded, generating output...")
            with Halo(text='Processing', spinner='dots') as spinner:
                response = generate_output([{"role": "user", "content": content}])
            if response:
                print("Output:", response.get('choices', [{}])[0].get('message', {}).get('content', 'No response generated'))
    elif command == 'set api key':
        set_api_key()
    elif command == 'change model':
        select_model()
    elif command.startswith('model '):
        new_model = command.split(' ', 1)[1]
        save_config('DEFAULT', 'Model', new_model)
        print(Fore.GREEN + f"Model changed to {new_model}")
    elif command.startswith('set max tokens '):
        try:
            max_tokens = int(command.split(' ', 3)[3])
            save_config('DEFAULT', 'MaxTokens', str(max_tokens))
            print(Fore.GREEN + f"Max tokens set to {max_tokens}")
        except ValueError:
            print(Fore.RED + "Invalid value for max tokens. Please enter a number.")
    elif command.startswith('set temperature '):
        try:
            temperature = float(command.split(' ', 3)[3])
            if 0 <= temperature <= 1:
                save_config('DEFAULT', 'Temperature', str(temperature))
                print(Fore.GREEN + f"Temperature set to {temperature}")
            else:
                print(Fore.RED + "Temperature must be between 0 and 1.")
        except ValueError:
            print(Fore.RED + "Invalid value for temperature. Please enter a number between 0 and 1.")
    else:
        # If not a command, treat as a message to the AI
        with Halo(text='Processing', spinner='dots') as spinner:
            response = generate_output([{"role": "user", "content": command}])
        if response:
            print("Assistant:", response.get('choices', [{}])[0].get('message', {}).get('content', 'No response generated'))

def main():
    """Main function to run the CLI tool."""
    load_config()
    print(Fore.CYAN + Style.BRIGHT + "Welcome to the OpenAI/Claude CLI Tool!")
    print(Fore.YELLOW + "Type 'help' to display command options or 'exit' to quit.")
    conversation = []
    while True:
        user_input = get_user_input()
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'help':
            help_menu()
        elif user_input.lower() == 'clear':
            clear_screen()
        else:
            process_command(user_input)
            if not user_input.startswith(('upload', 'set', 'change', 'model')):
                conversation.append({"role": "user", "content": user_input})
                if len(conversation) > 10:  # Keep last 10 messages for context
                    conversation = conversation[-10:]

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import os
import json
import time
from datetime import datetime
import readline  # For tab completion
import logging
import subprocess
import sys
import platform
import tkinter as tk
from tkinter import filedialog

# Auto-install dependencies if missing
def install_dependencies():
    required_packages = ["requests", "colorama", "openai"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing missing dependency: {package}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_dependencies()

# Ensure necessary imports
try:
    import requests
    from colorama import Fore, Style, init
    import openai
except ImportError as e:
    print(f"Failed to import module: {e}. Please ensure all dependencies are installed.")
    exit(1)

# Initialize colorama for coloring the text
init(autoreset=True)

# Set up logging for errors
logging.basicConfig(filename="openai_cli_errors.log", level=logging.ERROR)

# File paths for saving data
LOG_FILE = os.path.expanduser("~/.openai_log.txt")
PROMPT_FILE = os.path.expanduser("~/.openai_saved_prompts.txt")

# Define the mode variable
mode = "basic"

# List of available models
available_models = [
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4-turbo",
    "claude-3-opus-20240229",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307"
]

# Display welcome screen
def welcome_screen():
    print(Fore.CYAN + "Welcome to the OpenAI/Claude CLI Tool!")
    print(Fore.YELLOW + "Type 'help' to display command options or 'exit' to quit.")

# Load API keys
def load_api_keys():
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("OpenAI API key not found in environment variables.")
        openai_key = input("Please enter your OpenAI API key: ").strip()
    
    claude_key_path = "/Users/griffin/my_openai_project/Claude_API.txt"
    
    try:
        with open(claude_key_path, 'r') as f:
            claude_key = f.read().strip()
    except FileNotFoundError:
        print(f"Warning: Claude API key file not found at {claude_key_path}")
        claude_key = input("Please enter your Claude API key: ").strip()
    
    return openai_key, claude_key

def generate_output(messages, model="gpt-4-turbo", max_tokens=2048, temperature=0.7):
    openai_key, claude_key = load_api_keys()
    if model.startswith("gpt"):
        if not openai_key:
            print("Error: OpenAI API key not provided. Cannot use GPT models.")
            return None
        openai.api_key = openai_key
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error: {e}")
            return None
    elif model.startswith("claude"):
        if not claude_key:
            print("Error: Claude API key not found. Cannot use Claude models.")
            return None
        headers = {
            "Content-Type": "application/json",
            "x-api-key": claude_key,
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": model,
            "prompt": "\n\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages]) + "\n\nAssistant:",
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature
        }
        try:
            response = requests.post("https://api.anthropic.com/v1/complete", headers=headers, json=data)
            response.raise_for_status()
            return response.json()["completion"]
        except Exception as e:
            print(f"Error: {e}")
            return None
    else:
        print(f"Error: Unknown model {model}")
        return None

def upload_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(title="Select a file to upload")
    if file_path:
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            print(f"File uploaded successfully: {file_path}")
            return content
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    else:
        print("No file selected.")
        return None

def main():
    welcome_screen()
    print("Available models:", ", ".join(available_models))
    print(Fore.YELLOW + "Enter 'upload' to upload a file for analysis, or type your question directly.")
    model = input("Enter the model you want to use (default: gpt-4-turbo): ").strip() or "gpt-4-turbo"
    if model not in available_models:
        print(f"Warning: {model} is not in the list of available models. Proceeding anyway.")
    
    messages = []
    while True:
        user_input = input("You (type 'upload' to select a file, 'help' for options, or 'exit' to quit): ").strip()
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'help':
            print(Fore.GREEN + "Commands:")
            print("  upload - Upload a file for analysis")
            print("  exit - Exit the application")
            print("  [type text] - Send text directly to the AI model")
            continue
        elif user_input.lower() == 'upload':
            file_content = upload_file()
            if file_content:
                user_input = f"I'm uploading a file with the following content:\n\n{file_content}\n\nPlease analyze this content."
        
        messages.append({"role": "user", "content": user_input})
        response = generate_output(messages, model=model)
        
        if response:
            print("Assistant:", response)
            messages.append({"role": "assistant", "content": response})
            
            # Check if the response might be incomplete
            if len(response) >= 2048:  # Assuming 2048 is the max_tokens
                continuation = input("The response might be incomplete. Do you want to continue? (yes/no): ").strip().lower()
                while continuation == 'yes':
                    continuation_response = generate_output(messages + [{"role": "user", "content": "Please continue."}], model=model)
                    if continuation_response:
                        print("Assistant:", continuation_response)
                        messages.append({"role": "assistant", "content": continuation_response})
                        if len(continuation_response) < 2048:
                            break
                        continuation = input("Do you want to continue? (yes/no): ").strip().lower()
                    else:
                        print("Failed to generate continuation.")
                        break
        else:
            print("Failed to generate a response.")

if __name__ == "__main__":
    main()

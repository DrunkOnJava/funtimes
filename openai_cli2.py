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
    from openai import OpenAI
    
    client = OpenAI(api_key=openai_key)
except ImportError as e:
    print(f"Failed to import module: {e}. Please ensure all dependencies are installed.")
    exit(1)

# Initialize colorama for coloring the text
init(autoreset=True)

# Set up logging for errors and query responses
logging.basicConfig(filename="openai_cli_errors.log", level=logging.ERROR)
LOG_FILE = os.path.expanduser("~/.openai_log.txt")
PROMPT_FILE = os.path.expanduser("~/.openai_saved_prompts.txt")

# Cache mechanism for optimization
cache = {}

# API Key management
def load_api_keys():
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        openai_key = input("Please enter your OpenAI API key: ").strip()

    claude_key_path = "/Users/griffin/my_openai_project/Claude_API.txt"
    try:
        with open(claude_key_path, 'r') as f:
            claude_key = f.read().strip()
    except FileNotFoundError:
        claude_key = input("Please enter your Claude API key: ").strip()

    return openai_key, claude_key

# Generate output using OpenAI or Claude models
def generate_output(messages, model="gpt-4-turbo", max_tokens=2048, temperature=0.7):
    openai_key, claude_key = load_api_keys()

    if model.startswith("gpt"):
        if not openai_key:
            print("Error: OpenAI API key not provided.")
            return None
        try:
            response = client.chat.completions.create(model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature)
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error using OpenAI API: {e}")
            return None

    elif model.startswith("claude"):
        if not claude_key:
            print("Error: Claude API key not provided.")
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
            return response.json().completion
        except Exception as e:
            logging.error(f"Error using Claude API: {e}")
            return None
    else:
        print(f"Error: Unknown model {model}")
        return None

# Show real-time progress for long queries
def show_real_time_progress(query):
    print(f"Processing query: {query}")
    for i in range(10):
        time.sleep(0.2)
        print(f"Progress: {(i + 1) * 10}%", end="\r")
    print("\nQuery processed successfully!\n")

# Retry logic for failed queries
def retry_query(query_func, max_retries=3):
    attempts = 0
    while attempts < max_retries:
        try:
            return query_func()
        except Exception as e:
            logging.error(f"Attempt {attempts + 1} failed: {e}")
            attempts += 1
            if attempts == max_retries:
                print("Max retries reached. Could not complete the query.")
                return None

# Track and display average response time
def calculate_avg_response_time(total_time, query_count):
    return total_time / query_count if query_count > 0 else 0

# Upload file with tkinter GUI
def upload_file():
    root = tk.Tk()
    root.withdraw()
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

# Export session data to JSON or CSV
def export_session_data(session_data, format_type='json'):
    if format_type == 'json':
        with open("session_data.json", "w") as file:
            json.dump(session_data, file)
        print("Session data exported to session_data.json")
    elif format_type == 'csv':
        with open("session_data.csv", "w") as file:
            file.write("Query,Response\n")
            for entry in session_data:
                file.write(f"{entry['query']},{entry.response}\n")
        print("Session data exported to session_data.csv")

# Main CLI loop
def main():
    print(Fore.CYAN + "Welcome to the OpenAI/Claude CLI Tool!")
    available_models = [
        "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo",
        "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
    ]
    print("Available models:", ", ".join(available_models))

    model = input("Enter the model you want to use (default: gpt-4-turbo): ").strip() or "gpt-4-turbo"
    if model not in available_models:
        print(f"Warning: {model} is not in the list of available models. Proceeding anyway.")

    messages = []
    session_data = []
    total_time = 0

    while True:
        user_input = input("You (type 'upload' to select a file, or 'exit' to quit): ").strip()
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'upload':
            file_content = upload_file()
            if file_content:
                user_input = f"I'm uploading a file with the following content:\n\n{file_content}\n\nPlease analyze this content."

        messages.append({"role": "user", "content": user_input})
        start_time = time.time()
        response = retry_query(lambda: generate_output(messages, model=model))
        end_time = time.time()

        if response:
            total_time += (end_time - start_time)
            print("Assistant:", response)
            messages.append({"role": "assistant", "content": response})
            session_data.append({"query": user_input, "response": response})

            # Check if the response is truncated
            if len(response) >= 2048:
                continuation = input("The response might be incomplete. Continue? (yes/no): ").strip().lower()
                while continuation == 'yes':
                    continuation_response = retry_query(lambda: generate_output(messages + [{"role": "user", "content": "Please continue."}], model=model))
                    if continuation_response:
                        print("Assistant:", continuation_response)
                        messages.append({"role": "assistant", "content": continuation_response})
                        session_data.append({"query": "Please continue", "response": continuation_response})
                        if len(continuation_response) < 2048:
                            break
                        continuation = input("Continue? (yes/no): ").strip().lower()

        avg_response_time = calculate_avg_response_time(total_time, len(session_data))
        print(f"Average Response Time: {avg_response_time:.2f} seconds")

    export_session_data(session_data, format_type="json")
    print("Goodbye!")

if __name__ == "__main__":
    main()
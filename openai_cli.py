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

# Load API key from environment variable
def load_api_key():
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    else:
        print("Error: API key not found. Please set the OPENAI_API_KEY environment variable.")
        exit(1)

# Auto-install dependencies if missing
def install_dependencies():
    required_packages = ["requests", "colorama"]
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
    "text-davinci-003",
    "text-curie-001",
    "text-babbage-001",
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4-turbo"
]

# Display welcome screen
def welcome_screen():
    print(Fore.CYAN + r'''
      _____           _     _   _____  _      _____ 
     |  __ \         | |   | | |_   _|| |    |_   _|
     | |  | |  ___   | |_  | |   | |  | |      | |  
     | |  | | / _ \  | __| | |   | |  | |      | |  
     | |__| || (_) | | |_  | |  _| |_ | |____ _| |_ 
     |_____/  \___/   \__| |_| |_____||______|_____|
    ''' + Style.RESET_ALL)
    print(Fore.CYAN + "Welcome to the OpenAI CLI Tool!" + Style.RESET_ALL)
    print("This tool helps you interact with the OpenAI API easily.")
    print("Setting up the virtual environment...")

# Show a simple progress indicator
def show_progress(message="Processing"):
    for i in range(3):
        print(Fore.YELLOW + message + "." * i, end='\r')
        time.sleep(0.5)
    print(Style.RESET_ALL)

# Log interaction details
def log_interaction(prompt, response, start_time):
    response_time = time.time() - start_time
    log_entry = {
        "date": str(datetime.now()),
        "prompt": prompt,
        "response": response,
        "response_time": response_time
 }
    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    print(Fore.GREEN + f"Logged response time: {response_time:.2f} seconds" + Style.RESET_ALL)

# Fetch OpenAI response with error handling and retries
def fetch_openai_response_with_retries(api_key, model, prompt, temperature=0.7, max_tokens=150, retries=3):
    for attempt in range(retries):
        response = fetch_openai_response(api_key, model, prompt, temperature, max_tokens)
        if response:
            return response
        else:
            print(Fore.YELLOW + f"Retrying... Attempt {attempt + 1} of {retries}" + Style.RESET_ALL)
            time.sleep(2)
    print(Fore.RED + "Failed to fetch response after multiple attempts." + Style.RESET_ALL)
    return None

def fetch_openai_response(api_key, model, prompt, temperature=0.7, max_tokens=150):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            error_message = f"Error {response.status_code}: {response.text}"
            print(Fore.RED + error_message + Style.RESET_ALL)
            logging.error(error_message)
            return None
    except Exception as e:
        error_message = f"An error occurred: {e}"
        print(Fore.RED + error_message + Style.RESET_ALL)
        logging.error(error_message)
        return None

# Analyze a text file
def analyze_text_file():
    file_path = input(Fore.YELLOW + "Enter the path to the text file: " + Style.RESET_ALL)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        api_key = load_api_key()
        if not api_key:
            print(Fore.RED + "API key not found. Please set the API key first!" + Style.RESET_ALL)
        else:
            model = select_model()
            prompt = f"Provide a plan to optimize the following code, remove unused code, and improve the user experience:\n\n{content}"
            response = fetch_openai_response_with_retries(api_key, model, prompt)
            if response:
                print(Fore.GREEN + "Plan: " + response + Style.RESET_ALL)
                user_input = input(Fore.YELLOW + "Do you agree with the suggestions? (yes/no): " + Style.RESET_ALL).strip().lower()
                if user_input in ['yes', 'y']:
                    prompt = f"Implement the following improvements to the code:\n\n{content}\n\nPlan:\n{response}"
                    improved_code = fetch_openai_response_with_retries(api_key, model, prompt)
                    if improved_code:
                        print(Fore.GREEN + "Improved Code:\n" + improved_code + Style.RESET_ALL)
    else:
        print(Fore.RED + "File not found." + Style.RESET_ALL)

# Enter chat mode
def enter_chat_mode():
    print(Fore.CYAN + "Entering chat mode. Type 'exit', 'quit', or 'q' to leave." + Style.RESET_ALL)
    api_key = load_api_key()
    if not api_key:
        print(Fore.RED + "API key not found. Please set the API key first!" + Style.RESET_ALL)
        return
    model = select_model()

    while True:
        prompt = input(Fore.GREEN + "You: " + Style.RESET_ALL)
        if prompt.lower() in ['exit', 'quit', 'q']:
            print(Fore.CYAN + "Exiting chat mode..." + Style.RESET_ALL)
            break
        elif prompt.lower().startswith("read "):
            file_path = prompt[5:].strip()
            if os.path.isfile(file_path) and file_path.endswith(('.py', '.html', '.txt')):
                with open(file_path, 'r') as f:
                    content = f.read()
                print(Fore.YELLOW + f"Content of {file_path}:\n" + Style.RESET_ALL + content)
                prompt = f"Optimize this code, remove code that isn't being used or is useless, and improve the user experience overall:\n\n{content}"
            else:
                print(Fore.RED + "File not found or unsupported file type. Please provide a valid .py, .html, or .txt file." + Style.RESET_ALL)
        response = fetch_openai_response_with_retries(api_key, model, prompt)
        if response:
            print(Fore.BLUE + "OpenAI: " + response + Style.RESET_ALL)

# View logs
def view_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            logs = f.readlines()
        for log in logs:
            print(log)
    else:
        print(Fore.RED + "No logs found." + Style.RESET_ALL)

# Display the main menu
def display_menu():
    print(Fore.CYAN + "\nMain Menu" + Style.RESET_ALL)
    print(Fore.YELLOW + "1. View Logs" + Style.RESET_ALL)
    print(Fore.YELLOW + "2. Analyze Text File" + Style.RESET_ALL)
    print(Fore.YELLOW + "3. Enter Chat Mode" + Style.RESET_ALL)
    print(Fore.YELLOW + "4. Switch Mode" + Style.RESET_ALL)
    print(Fore.YELLOW + "0. Exit" + Style.RESET_ALL)

# Switch between basic and advanced modes
def switch_mode():
    global mode
    mode = "advanced" if mode == "basic" else "basic"
    print(Fore.GREEN + f"Switched to {mode.title()} Mode." + Style.RESET_ALL)

# Select model from available models
def select_model():
    print(Fore.CYAN + "\nAvailable Models:" + Style.RESET_ALL)
    for i, model in enumerate(available_models, 1):
        print(Fore.YELLOW + f"{i}. {model}" + Style.RESET_ALL)
    while True:
        try:
            choice = int(input(Fore.YELLOW + "Enter the number of the model you want to use: " + Style.RESET_ALL))
            if 1 <= choice <= len(available_models):
                return available_models[choice - 1]
            else:
                print(Fore.RED + "Invalid choice. Please select a valid number." + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "Invalid input. Please enter a number." + Style.RESET_ALL)

# Main function
def main():
    welcome_screen()
    print("Step 1: Checking and installing dependencies...")
    install_dependencies()
    print("Step 2: Initializing colorama...")
    init(autoreset=True)
    print("Step 3: Setting up logging...")
    logging.basicConfig(filename="openai_cli_errors.log", level=logging.ERROR)
    print("Step 4: Loading API key...")
    api_key = load_api_key()
    print("Step 5: Setup complete. Ready to use the OpenAI CLI Tool.")

    while True:
        display_menu()
        choice = input(Fore.YELLOW + "Choose an option: " + Style.RESET_ALL).lower()

        if choice == "1":
            view_logs()

        elif choice == "2":
            analyze_text_file()

        elif choice == "3":
            enter_chat_mode()

        elif choice == "4":
            switch_mode()

        elif choice == "0":
            print(Fore.CYAN + "Exiting..." + Style.RESET_ALL)
            break

        else:
            print(Fore.RED + "Invalid choice. Please select a valid option." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
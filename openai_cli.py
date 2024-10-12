#!/usr/bin/env python3
import os
import json
import time
from datetime import datetime
import readline  # For tab completion

# Ensure necessary imports
try:
    import requests  # type: ignore
except ImportError:
    print("The 'requests' module is not installed. Please install it using 'pip install requests'.")
    exit(1)

try:
    from colorama import Fore, Style, init  # type: ignore
except ImportError:
    print("The 'colorama' module is not installed. Please install it using 'pip install colorama'.")
    exit(1)

# Initialize colorama for coloring the text
init(autoreset=True)

# File paths for saving data
API_KEY_FILE = os.path.expanduser("~/.openai_api_keys")
LOG_FILE = os.path.expanduser("~/.openai_log.txt")
PROMPT_FILE = os.path.expanduser("~/.openai_saved_prompts.txt")
SESSION_FILE = os.path.expanduser("~/.openai_session.json")
THEME_FILE = os.path.expanduser("~/.openai_theme.json")

# Command history list
command_history = []

# Mode options
mode = "basic"
theme = "dark"

# Tab completion for commands and options
COMMANDS = ['set api key', 'prompt', 'save', 'load', 'logs', 'help', 'quit', 'mode', 'theme', 'clear logs']
readline.set_completer_delims(' \t\n=')
readline.parse_and_bind("tab: complete")

def completer(text, state):
    options = [cmd for cmd in COMMANDS if cmd.startswith(text)]
    if state < len(options):
        return options[state]
    return None

readline.set_completer(completer)

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
    print(Fore.YELLOW + "Tip: Use 'Q' to quit and 'R' to repeat the last prompt." + Style.RESET_ALL)

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

# Save API key
def save_api_key(api_name, api_key):
    try:
        if not os.path.exists(API_KEY_FILE):
            api_keys = {}
        else:
            with open(API_KEY_FILE, 'r') as f:
                api_keys = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        api_keys = {}

    api_keys[api_name] = api_key
    with open(API_KEY_FILE, 'w') as f:
        json.dump(api_keys, f)

    print(Fore.GREEN + f"API key for '{api_name}' saved successfully." + Style.RESET_ALL)

# Load API key
def load_api_key(api_name):
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'r') as f:
            api_keys = json.load(f)
        return api_keys.get(api_name, None)
    else:
        return None

# Interact with OpenAI API
def interact_with_openai(api_key, model, prompt, temperature=0.7, max_tokens=150, top_p=1.0):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    # Initial request setup
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
        "n": 1
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        print(Fore.RED + "Error: Failed to fetch response from OpenAI." + Style.RESET_ALL)
        return None

# Save a prompt
def save_prompt(prompt):
    if not os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, 'w') as f:
            json.dump([prompt], f)
    else:
        with open(PROMPT_FILE, 'r+') as f:
            prompts = json.load(f)
            prompts.append(prompt)
            f.seek(0)
            json.dump(prompts, f)
    print(Fore.GREEN + "Prompt saved successfully." + Style.RESET_ALL)

# Load and display saved prompts
def load_prompts():
    if os.path.exists(PROMPT_FILE):
        with open(PROMPT_FILE, 'r') as f:
            prompts = json.load(f)
        print(Fore.CYAN + "Saved Prompts:" + Style.RESET_ALL)
        for i, prompt in enumerate(prompts, 1):
            print(f"{i}. {prompt}")
    else:
        print(Fore.RED + "No saved prompts found." + Style.RESET_ALL)

# Analyze a text file
def analyze_text_file():
    file_path = input(Fore.YELLOW + "Enter the path to the text file: " + Style.RESET_ALL)
    if os.path.isfile(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        api_name = input(Fore.YELLOW + "Enter the API key name to use: " + Style.RESET_ALL)
        api_key = load_api_key(api_name)
        if not api_key:
            print(Fore.RED + "API key not found. Please set the API key first!" + Style.RESET_ALL)
        else:
            model = input(Fore.YELLOW + "Enter the model (e.g., gpt-4): " + Style.RESET_ALL)
            prompt = f"Summarize the following text:\n\n{content}"
            response = interact_with_openai(api_key, model, prompt)
            print(Fore.GREEN + "Response: " + response + Style.RESET_ALL)
    else:
        print(Fore.RED + "File not found." + Style.RESET_ALL)

# Enter chat mode
def enter_chat_mode():
    print(Fore.CYAN + "Entering chat mode. Type 'exit' to quit." + Style.RESET_ALL)
    api_name = input(Fore.YELLOW + "Enter the API key name to use: " + Style.RESET_ALL)
    api_key = load_api_key(api_name)
    if not api_key:
        print(Fore.RED + "API key not found. Please set the API key first!" + Style.RESET_ALL)
        return
    model = input(Fore.YELLOW + "Enter the model (e.g., gpt-4): " + Style.RESET_ALL)

    while True:
        prompt = input(Fore.YELLOW + "You: " + Style.RESET_ALL)
        if prompt.lower() in ['exit', 'quit', 'q']:
            print(Fore.GREEN + "Exiting chat mode..." + Style.RESET_ALL)
            break
        response = interact_with_openai(api_key, model, prompt)
        if response:
            print(Fore.CYAN + "OpenAI: " + response + Style.RESET_ALL)

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
    print(Fore.YELLOW + "1. Set API Key" + Style.RESET_ALL)
    print(Fore.YELLOW + "2. Enter a Prompt (P)" + Style.RESET_ALL)
    print(Fore.YELLOW + "3. Save/Load Prompts (S)" + Style.RESET_ALL)
    print(Fore.YELLOW + "4. View Logs (L)" + Style.RESET_ALL)
    print(Fore.YELLOW + "5. Analyze a Text File" + Style.RESET_ALL)
    print(Fore.YELLOW + "6. Enter Chat Mode" + Style.RESET_ALL)
    print(Fore.YELLOW + "7. Change Mode" + Style.RESET_ALL)
    print(Fore.YELLOW + "8. Theme Settings" + Style.RESET_ALL)
    print(Fore.YELLOW + "9. Quit (Q)" + Style.RESET_ALL)

# Switch between basic and advanced modes
def switch_mode():
    global mode
    mode = "advanced" if mode == "basic" else "basic"
    print(Fore.GREEN + f"Switched to {mode.title()} Mode." + Style.RESET_ALL)

# Set theme (light or dark)
def set_theme():
    global theme
    choice = input(Fore.YELLOW + "Choose a theme (light/dark): " + Style.RESET_ALL).lower()
    if choice in ["light", "dark"]:
        theme = choice
        with open(THEME_FILE, 'w') as f:
            json.dump({"theme": theme}, f)
        print(Fore.GREEN + f"Switched to {theme} theme." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Invalid choice. Defaulting to dark theme." + Style.RESET_ALL)

# Main function
def main():
    welcome_screen()

    while True:
        display_menu()
        choice = input(Fore.YELLOW + "Choose an option: " + Style.RESET_ALL).lower()

        if choice in ["1", "set api key"]:
            api_name = input(Fore.YELLOW + "Enter a name for this API key: " + Style.RESET_ALL)
            api_key = input(Fore.YELLOW + "Enter your OpenAI API Key: " + Style.RESET_ALL)
            save_api_key(api_name, api_key)

        elif choice in ["2", "p", "prompt"]:
            api_name = input(Fore.YELLOW + "Enter the API key name to use: " + Style.RESET_ALL)
            api_key = load_api_key(api_name)
            if not api_key:
                print(Fore.RED + "API key not found. Please set the API key first!" + Style.RESET_ALL)
            else:
                model = input(Fore.YELLOW + "Enter the model (e.g., gpt-4): " + Style.RESET_ALL)
                prompt = input(Fore.YELLOW + "Enter your prompt: " + Style.RESET_ALL)
                temperature = float(input(Fore.YELLOW + "Set temperature (default 0.7): " + Style.RESET_ALL) or 0.7)
                max_tokens = int(input(Fore.YELLOW + "Set max tokens (default 150): " + Style.RESET_ALL) or 150)
                response = interact_with_openai(api_key, model, prompt, temperature, max_tokens)
                print(Fore.GREEN + "Response: " + response + Style.RESET_ALL)

        elif choice == "3":
            sub_choice = input(Fore.YELLOW + "Would you like to (1) Save a new prompt or (2) Load existing prompts? " + Style.RESET_ALL)
            if sub_choice == "1":
                new_prompt = input(Fore.YELLOW + "Enter the prompt you'd like to save: " + Style.RESET_ALL)
                save_prompt(new_prompt)
            elif sub_choice == "2":
                load_prompts()
            else:
                print(Fore.RED + "Invalid choice. Please select 1 or 2." + Style.RESET_ALL)

        elif choice == "4":
            view_logs()

        elif choice == "5":
            analyze_text_file()

        elif choice == "6":
            enter_chat_mode()

        elif choice == "7":
            switch_mode()

        elif choice == "8":
            set_theme()

        elif choice in ["9", "q"]:
            print(Fore.GREEN + "Goodbye!" + Style.RESET_ALL)
            break

if __name__ == "__main__":
    main()
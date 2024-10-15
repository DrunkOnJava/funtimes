#!/usr/bin/env python3

import os
import json
import time
import sys
import logging
import argparse
from datetime import datetime
import requests
from colorama import Fore, Style, init
from tqdm import tqdm
from getpass import getpass

# Constants
CONFIG_FILE = os.path.expanduser("~/.openai_claude_cli_config.json")
AVAILABLE_MODELS = [
    "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo",
    "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
]

# Initialize colorama
init(autoreset=True)

class ConfigWizard:
    def __init__(self):
        self.config = {}

    def run(self):
        print(Fore.CYAN + "Welcome to the OpenAI/Claude CLI Tool Configuration Wizard!")
        self.config['openai_key'] = getpass("Enter your OpenAI API key: ")
        self.config['claude_key'] = getpass("Enter your Claude API key: ")
        self.config['default_model'] = input("Enter your default model: ")
        self.config['user_name'] = input("Enter your name: ")
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f)
        print(Fore.GREEN + "Configuration saved successfully!")

class UserProfile:
    def __init__(self, name):
        self.name = name
        self.config_file = os.path.expanduser(f"~/.openai_claude_cli_{name}.json")
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

class PluginManager:
    def __init__(self):
        self.plugins = {}

    def load_plugins(self):
        plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')
        if not os.path.isdir(plugin_dir):
            print(Fore.YELLOW + "No plugins directory found. Skipping plugin loading.")
            return
        
        for filename in os.listdir(plugin_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                module = __import__(f'plugins.{module_name}', fromlist=[''])
                if hasattr(module, 'register_plugin'):
                    module.register_plugin(self)

    def register_plugin(self, name, plugin):
        self.plugins[name] = plugin

    def execute_plugin(self, name, *args, **kwargs):
        if name in self.plugins:
            return self.plugins[name](*args, **kwargs)
        else:
            raise ValueError(f"Plugin '{name}' not found")

def setup_argparse():
    parser = argparse.ArgumentParser(description="OpenAI/Claude CLI Tool")
    parser.add_argument('--config', type=str, help='Path to custom config file')
    parser.add_argument('--profile', type=str, help='User profile name')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    return parser

def setup_logging(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(filename='cli_tool.log', level=level, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

class Config:
    def __init__(self, config_file=None, profile=None):
        self.config_file = config_file or CONFIG_FILE
        self.profile = profile
        self.load_config()

    def load_config(self):
        if self.profile:
            self.config_file = os.path.expanduser(f"~/.openai_claude_cli_{self.profile}.json")
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}
            wizard = ConfigWizard()
            wizard.run()
            self.config = wizard.config

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

class ConversationManager:
    def __init__(self, config):
        self.config = config
        self.conversations = {}
        self.current_conversation_id = None

    def start_new_conversation(self):
        conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.conversations[conversation_id] = []
        self.current_conversation_id = conversation_id
        return conversation_id

    def add_message(self, role, content):
        if self.current_conversation_id is None:
            self.start_new_conversation()
        self.conversations[self.current_conversation_id].append({"role": role, "content": content})

    def get_current_conversation(self):
        return self.conversations.get(self.current_conversation_id, [])

    def save_conversation(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.get_current_conversation(), f, indent=2)
        print(Fore.GREEN + f"Conversation saved to {filename}")

    def load_conversation(self, filename):
        try:
            with open(filename, 'r') as f:
                conversation = json.load(f)
            conversation_id = self.start_new_conversation()
            self.conversations[conversation_id] = conversation
            print(Fore.GREEN + f"Conversation loaded from {filename}")
        except FileNotFoundError:
            print(Fore.RED + f"File {filename} not found.")
        except json.JSONDecodeError:
            print(Fore.RED + "Error decoding JSON. Please check the file format.")

    def branch_conversation(self):
        if self.current_conversation_id is None:
            print(Fore.RED + "No active conversation to branch from.")
            return None
        
        new_conversation_id = self.start_new_conversation()
        self.conversations[new_conversation_id] = self.get_current_conversation().copy()
        print(Fore.GREEN + f"Created new branch: {new_conversation_id}")
        return new_conversation_id

    def summarize_conversation(self):
        conversation = self.get_current_conversation()
        if not conversation:
            return "No conversation to summarize."
        
        summary = f"Conversation Summary:\n"
        summary += f"Total messages: {len(conversation)}\n"
        summary += f"User messages: {sum(1 for msg in conversation if msg['role'] == 'user')}\n"
        summary += f"Assistant messages: {sum(1 for msg in conversation if msg['role'] == 'assistant')}\n"
        summary += f"Last 3 exchanges:\n"
        for msg in conversation[-6:]:
            summary += f"  {msg['role'].capitalize()}: {msg['content'][:50]}...\n"
        
        return summary

def show_progress(seconds, message):
    """Show a progress bar for a given number of seconds."""
    for _ in tqdm(range(seconds), desc=message, ncols=70, bar_format='{l_bar}{bar}'):
        time.sleep(1)

def retry_query(func, max_retries=3):
    """Retry a function call with exponential backoff."""
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:
                raise e
            wait_time = 2 ** i
            print(Fore.YELLOW + f"Error occurred. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

def generate_output(config, messages, model=None, max_tokens=2048, temperature=0.7):
    """Generate output using OpenAI or Claude models."""
    if not model:
        model = config.get('default_model')
    
    if model.startswith("gpt"):
        if not config.get('openai_key'):
            print(Fore.RED + "Error: OpenAI API key not provided. Please set it first.")
            return None
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.get('openai_key')}"
        }
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logging.error(f"Error using OpenAI API: {e}")
            print(Fore.RED + f"Error: {str(e)}")
            return None
    elif model.startswith("claude"):
        if not config.get('claude_key'):
            print(Fore.RED + "Error: Claude API key not provided. Please set it first.")
            return None
        headers = {
            "Content-Type": "application/json",
            "x-api-key": config.get('claude_key'),
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        try:
            response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=data)
            response.raise_for_status()
            return response.json()["content"][0]["text"]
        except Exception as e:
            logging.error(f"Error using Claude API: {e}")
            print(Fore.RED + f"Error: {str(e)}")

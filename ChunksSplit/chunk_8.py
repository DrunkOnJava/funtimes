if __name__ == "__main__":
    main_menu()



# File system browsing for file uploads
def browse_filesystem():
    file_path = input_dialog(title='Browse Files', text='Enter the path to the file you wish to upload:')
    if file_path:
        if validate_file_type(file_path):
            console.print(f"[green]File path: {file_path}[/green]")
            return file_path
        else:
            console.print("[red]Invalid file type or file size too large.[/red]")
    return None

# Model Management Features
class ModelManager:
    def __init__(self, config):
        self.config = config
        self.usage_stats = {model: {'requests': 0, 'tokens': 0} for model in AVAILABLE_MODELS}

    def switch_model(self, model_name):
        if model_name in AVAILABLE_MODELS:
            self.config.set('default_model', model_name)
            console.print(f"[bold green]Switched to model: {model_name}[/bold green]")
        else:
            console.print(f"[red]Error: Model {model_name} is not available.[/red]")

    def fine_tune_model(self, dataset_path, model_name=None, epochs=3, learning_rate=0.001):
        model = model_name or self.config.get('default_model')
        if not os.path.exists(dataset_path):
            console.print(f"[red]Dataset not found: {dataset_path}[/red]")
            return
        if __name__ == "__main__":
            main()
        console.print(f"[yellow]Fine-tuning model {model} with dataset {dataset_path}...[/yellow]")
        try:
            response = requests.post(
                f"https://api.openai.com/v1/fine-tunes",
                headers={"Authorization": f"Bearer {self.config.get('openai_key')}"},
                json={"model": model, "dataset": dataset_path, "epochs": epochs, "learning_rate": learning_rate}
            )
            response.raise_for_status()
            console.print(f"[green]Model {model} successfully fine-tuned![/green]")
        except Exception as e:
            console.print(f"[red]Fine-tuning failed: {e}[/red]")

    def compare_models(self, user_input, models=None):
        models = models or AVAILABLE_MODELS
        responses = {}
        for model in models:
            self.config.set('default_model', model)
            console.print(f"[yellow]Generating response from {model}...[/yellow]")
            response = chat_manager.generate_response(user_input)
            responses[model] = response
        self.display_comparison(responses)

    def display_comparison(self, responses):
        for model, response in responses.items():
            console.print(f"[bold cyan]Model: {model}[/bold cyan]")
            console.print(f"{response}")

    def track_usage(self, model, tokens):
        self.usage_stats[model]['requests'] += 1
        self.usage_stats[model]['tokens'] += tokens

    def display_usage_stats(self):
        console.print("[bold cyan]Model Usage Statistics:[/bold cyan]")
        for model, stats in self.usage_stats.items():
            console.print(f"[yellow]{model}[/yellow] - Requests: {stats['requests']}, Tokens: {stats['tokens']}")

    def measure_performance(self, func, model, *args, **kwargs):
        start_time = time.time()
        response = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        tokens_used = len(response)  # Simplified token calculation
        self.track_usage(model, tokens_used)
        console.print(f"[cyan]Model: {model}, Response Time: {elapsed_time:.2f} seconds, Tokens Used: {tokens_used}[/cyan]")
        return response

    def autoswitch_model(self, user_input):
        if len(user_input) > 1000 or 'complex' in user_input:
            console.print("[yellow]Switching to a more powerful model...[/yellow]")
            self.switch_model("gpt-4")
        else:
            self.switch_model("gpt-3.5-turbo")

    def recover_from_failure(self, user_input):
        chat_manager = ChatManager(self.config)  # Define chat_manager here
        try:
            response = chat_manager.generate_response(user_input)
            return response
        except Exception as e:
            console.print(f"[red]Model failed: {e}. Switching to backup model...[/red]")
            self.switch_model('gpt-3.5-turbo')
            return chat_manager.generate_response(user_input)

# Chat Management Features
class ChatManager:
    def __init__(self, config):
        self.config = config
        self.conversation = []

    def add_message(self, role, content):
        self.conversation.append({"role": role, "content": content})

    def get_conversation(self):
        return self.conversation

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
            return response.json().choices[0].message.content
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
            return response.json().completion
        except Exception as e:
            return f"[red]Error occurred: {e}[/red]"


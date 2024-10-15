    response = get_model_response(user_input)
    console.print(f"[green]Model response:[/green] {response}")

def get_model_response(user_input):
    try:
        response = client.completions.create(model="gpt-4-turbo",  # Use the appropriate model
        prompt=user_input,
        max_tokens=150)
        return response.choices[0].text.strip()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return "An error occurred while fetching the response."

def main_with_loading_bars():
    console.print("\n[bold cyan]Testing Progress Indicators and Loading Bars[/bold cyan]")

    # Example: Simulating loading a large file
    analyze_file_with_loading_bar("large_document.txt")

    # Example: Simulating a chat session with loading bars
    chat_with_loading_bars("This is a test input for the chat session.")

    # Return to main menu after tests
    main_menu()

def analyze_file(file_path):
    _, ext = os.path.splitext(file_path)
    if ext not in SUPPORTED_FORMATS:
        console.print(f"[red]Unsupported file format: {ext}[/red]")
        return
    if ext == '.py':
        analyze_python_file(file_path)
    else:
        console.print(f"Analyzing {ext} file content:")
        with open(file_path, 'r') as file:
            content = file.read()
            console.print(content)

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

# Command History Search
def search_command_history(history_file, search_term):
    try:
        with open(history_file, 'r') as file:
            history = file.readlines()
        matching_commands = [cmd.strip() for cmd in history if search_term in cmd]
        return matching_commands if matching_commands else ["[yellow]No matching commands found.[/yellow]"]
    except OSError as e:
        console.print(f"[red]Error reading command history: {e}[/red]")
        return []

# File Type Validation and Size Handling
def validate_file_type(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() not in SUPPORTED_FORMATS:
        console.print(f"[red]Unsupported file format: {file_extension}[/red]")
        return False
    if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10MB size limit
        console.print(f"[yellow]Warning: Large file detected, processing may take longer.[/yellow]")
    return True

# Large Input/Output Handling Functions

def chunk_text(text, max_chunk_size=5000):
    """
    Breaks the text into smaller chunks while respecting sentence boundaries.
    """
    sentences = text.split('.')
    current_chunk = ""
    chunks = []

    for sentence in sentences:
        sentence = sentence.strip() + '.'
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:  # Append the last chunk
        chunks.append(current_chunk.strip())

    return chunks

def chunk_file(file_content, max_chunk_size=5000):
    """
    Splits large files into smaller chunks based on line or paragraph boundaries.
    """
    paragraphs = file_content.split('\n\n')
    current_chunk = ""
    chunks = []

    for paragraph in paragraphs:
        paragraph = paragraph.strip() + '\n\n'
        if len(current_chunk) + len(paragraph) <= max_chunk_size:
            current_chunk += paragraph
        else:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())


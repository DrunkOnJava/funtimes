import re

file_path = "/Users/griffin/my_openai_project/integrated_tool2.py"

with open(file_path, 'r') as file:
    content = file.read()

# Update OpenAI import
content = re.sub(r'import openai', 'from openai import OpenAI', content)

# Update generate_output function
new_function = '''
def generate_output(messages, config, model=None, max_tokens=2048, temperature=0.7):
    if not model:
        model = config.get('default_model')
    
    if model.startswith("gpt"):
        client = OpenAI(api_key=config.get('openai_key'))
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logging.error(f"Error using OpenAI API: {e}")
            print(Fore.RED + f"Error: {str(e)}")
            return None
    elif model.startswith("claude"):
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
            return None
    else:
        print(Fore.RED + f"Error: Unknown model {model}")
        return None
'''

content = re.sub(r'def generate_output\(.*?\).*?return None\n', new_function, content, flags=re.DOTALL)

with open(file_path, 'w') as file:
    file.write(content)

print("File updated successfully!")
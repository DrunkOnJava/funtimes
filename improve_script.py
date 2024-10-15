import subprocess
import sys

def run_linter_and_type_checker(file_path):
    # Running flake8 to check for PEP8 compliance and common errors
    print("Running flake8 for style guide enforcement and basic checks...")
    result_flake8 = subprocess.run(['flake8', file_path], text=True, capture_output=True)
    if result_flake8.stdout:
        print("flake8 output:")
        print(result_flake8.stdout)
    if result_flake8.stderr:
        print("flake8 errors:")
        print(result_flake8.stderr)

    print("\n")

    # Running mypy for static type checking
    print("Running mypy for static type checking...")
    result_mypy = subprocess.run(['mypy', file_path], text=True, capture_output=True)
    if result_mypy.stdout:
        print("mypy output:")
        print(result_mypy.stdout)
    if result_mypy.stderr:
        print("mypy errors:")
        print(result_mypy.stderr)

if __name__ == "__main__":
    # Path to the Python script to analyze
    file_path = "/users/griffin/my_openai_project/untested_script.py"

    if len(sys.argv) > 1:
        file_path = sys.argv[1]  # Allows for a command line argument to specify the file

    run_linter_and_type_checker(file_path)

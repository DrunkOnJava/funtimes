#!/bin/bash

# Define the file path
FILE_PATH="/Users/griffin/my_openai_project/integrated_tool2.py"

# Backup the original file
cp "$FILE_PATH" "${FILE_PATH}.backup"

# Run the Python script to update the file
python3 update_script.py

# Run pip to upgrade openai
pip install --upgrade openai

# Run the modified script
python3 "$FILE_PATH"

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo "Script ran successfully!"
else
    echo "Script encountered an error. Restoring original file..."
    mv "${FILE_PATH}.backup" "$FILE_PATH"
    echo "Original file restored. Please check the script manually."
fi
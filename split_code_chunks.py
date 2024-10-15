import os

def create_chunks(file_path, output_folder, lines_per_chunk=150):
    try:
        # Read the full code from the input file
        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        chunk = []
        chunk_num = 1
        current_line_count = 0

        for line in lines:
            chunk.append(line)
            current_line_count += 1

            # Create a new chunk file once the specified lines per chunk is reached
            if current_line_count >= lines_per_chunk and line.strip() == '':
                chunk_file_path = os.path.join(output_folder, f'chunk_{chunk_num}.py')
                with open(chunk_file_path, 'w') as chunk_file:
                    chunk_file.writelines(chunk)
                chunk_num += 1
                chunk = []
                current_line_count = 0

        # Handle the final chunk if it didn't reach the chunk size limit
        if chunk:
            chunk_file_path = os.path.join(output_folder, f'chunk_{chunk_num}.py')
            with open(chunk_file_path, 'w') as chunk_file:
                chunk_file.writelines(chunk)

        print(f"Code split into {chunk_num} chunks and saved to '{output_folder}'.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Main entry point
if __name__ == '__main__':
    try:
        # Prompt for file paths and folder name
        input_file = input("Enter the path to your code file: ").strip()
        output_directory = input("Enter the path for the output folder: ").strip()

        # Check if the input file exists
        if not os.path.isfile(input_file):
            print("The specified input file does not exist. Please check the file path and try again.")
        else:
            create_chunks(input_file, output_directory)
            
    except KeyboardInterrupt:
        print("\nProcess interrupted by the user.")

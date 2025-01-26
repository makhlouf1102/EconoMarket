import json
import os

def merge_json_files(directory, output_file):
    try:
        merged_data = []

        # Iterate through all files in the directory
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                file_path = os.path.join(directory, filename)
                
                # Read the JSON file
                with open(file_path, 'r', encoding='utf-8') as file:
                    try:
                        data = json.load(file)

                        # Check if the data is a list
                        if isinstance(data, list):
                            merged_data.extend(data)
                        else:
                            print(f"File {filename} does not contain a JSON array and will be skipped.")
                    except json.JSONDecodeError:
                        print(f"File {filename} is not a valid JSON file and will be skipped.")

        # Write the merged data to the output file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(merged_data, file, indent=4, ensure_ascii=False)

        print(f"Merged {len(merged_data)} items into {output_file}.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Replace 'json_directory' with the path to the directory containing JSON files
# Replace 'merged_output.json' with the desired output file name
merge_json_files('json_directory', 'products.json')

import json

def add_store_field_to_json(file_path, store_name="None"):
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Check if the data is a list of items
        if isinstance(data, list):
            # Add 'store' field to each item
            for item in data:
                item['store'] = store_name
        else:
            print("The JSON file does not contain a list of items.")
            return

        # Write the modified data back to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        print("The 'store' field has been added to all items.")

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Replace 'your_file.json' with the path to your JSON file
add_store_field_to_json('products_pharmaprix.json', "PHARMAPRIX")

import json

def remove_items_with_empty_price(input_file, output_file):
    try:
        # Load the JSON data from the file
        with open(input_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Ensure the data is a list
        if not isinstance(data, list):
            print("Invalid JSON structure: Expected a list of items.")
            return

        # Filter out items with empty 'price_text'
        filtered_data = [item for item in data if item.get("price_text")]

        # Save the filtered data back to a new JSON file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(filtered_data, file, indent=4, ensure_ascii=False)

        print(f"Filtered data saved to {output_file}. Total items: {len(filtered_data)}")

    except FileNotFoundError:
        print(f"File not found: {input_file}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {input_file}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Replace 'input.json' and 'output.json' with your file paths
remove_items_with_empty_price('data/data_.json', 'data/data.json')

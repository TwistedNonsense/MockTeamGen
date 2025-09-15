import csv
import json
import sys

def convert_csv_to_json(csv_filepath, json_filepath):
    """
    Converts a CSV file to a JSON file.
    Each row in the CSV becomes an object in a JSON array.
    """
    # Check if the file paths are valid
    if not csv_filepath or not json_filepath:
        print("Error: Missing file paths. Please provide both input CSV and output JSON file names.")
        return

    data = []
    
    # Read the CSV file
    try:
        with open(csv_filepath, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: The file '{csv_filepath}' was not found.")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return

    # Write the data to a JSON file
    try:
        with open(json_filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(data, jsonfile, indent=4)
        print(f"Conversion successful! Data from '{csv_filepath}' saved to '{json_filepath}'.")
    except Exception as e:
        print(f"An error occurred while writing the JSON file: {e}")

if __name__ == "__main__":
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python your_script_name.py <input.csv> <output.json>")
    else:
        # sys.argv[0] is the script name itself
        # sys.argv[1] is the first argument (input file)
        # sys.argv[2] is the second argument (output file)
        input_csv = sys.argv[1]
        output_json = sys.argv[2]
        
        convert_csv_to_json(input_csv, output_json)

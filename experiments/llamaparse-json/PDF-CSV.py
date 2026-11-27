import nest_asyncio
import json
import re
import csv
import os
from llama_parse import LlamaParse

# Apply nest_asyncio for event loop compatibility
nest_asyncio.apply()

def initialize_parser(api_key, result_type="markdown", num_workers=6, language="en", verbose=True):
    """
    Initialize the LlamaParse parser with specified parameters.
    """
    return LlamaParse(
        api_key=api_key,
        result_type=result_type,
        num_workers=num_workers,
        language=language,
        verbose=verbose,
        parsing_instruction=(
            "Consider Yourself as a Professional Data analyst. "
            "Parse all The Table from the pdf page and give the response in a structured manner. "
            "If you are not much confident about the table header, put any default column name "
            "which may represent the column values. I want it in a stringified JSON-like structure "
            "so that it preserves the structural information from the table."
        ),
    )


def extract_markdown_text(parser, file_paths):
    """
    Load and extract markdown text from the provided files using the parser.
    """
    docs = parser.load_data(file_paths)
    markdown_content = ''.join([doc.text for doc in docs])
    return markdown_content


def extract_json_fragments(markdown_content):
    """
    Extract JSON-like fragments from the markdown content.
    """
    return re.findall(r'```json\n(.*?)\n```', markdown_content, re.DOTALL)


def combine_fragments_to_json(json_fragments):
    """
    Combine extracted JSON fragments into a unified JSON structure.
    """
    merged_json = {"data_sections": []}
    for fragment in json_fragments:
        try:
            parsed_fragment = json.loads(fragment)
            merged_json["data_sections"].append(parsed_fragment)
        except json.JSONDecodeError:
            pass  # Skip invalid fragments
    return merged_json


def save_json_to_file(data, output_path):
    """
    Save the JSON data to a file.
    """
    with open(output_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"JSON file saved to: {output_path}")


def json_to_csv(data, output_dir="csv_tables"):
    """
    Convert JSON data to CSV files.
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    table_count = 0  # To keep track of the number of tables extracted

    for idx, section in enumerate(data.get("data_sections", [])):
        # Collect potential tables from various keys
        potential_tables = []

        if isinstance(section, dict):
            for key, value in section.items():
                if isinstance(value, list):
                    potential_tables.append(value)
                elif isinstance(value, dict) and "Table" in value:
                    potential_tables.append(value["Table"])

        for table in potential_tables:
            if isinstance(table, list) and len(table) > 0:
                # Infer headers and rows
                if isinstance(table[0], dict):
                    headers = table[0].keys()
                    rows = [[row.get(h, "") for h in headers] for row in table]
                elif isinstance(table[0], list):
                    headers = [f"Column{i + 1}" for i in range(len(table[0]))]
                    rows = table
                else:
                    headers = [f"Column{i + 1}" for i in range(len(table))]
                    rows = [table]

                # Save table as CSV
                output_csv_path = os.path.join(output_dir, f"table_{table_count + 1}.csv")
                with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
                    writer = csv.writer(csv_file)
                    writer.writerow(headers)  # Write headers
                    writer.writerows(rows)    # Write rows

                print(f"CSV file saved: {output_csv_path}")
                table_count += 1
            else:
                print(f"Skipping non-standard or empty table at section {idx + 1}.")

    print(f"Total tables extracted: {table_count}")


# Main Function to Orchestrate the Workflow
def main():
    # Step 1: Initialize parser
    parser = initialize_parser(api_key="YOUR_API_KEY")

    # Step 2: Extract markdown content
    markdown_content = extract_markdown_text(parser, ["input document.pdf"])

    # Step 3: Extract JSON fragments from markdown content
    json_fragments = extract_json_fragments(markdown_content)

    # Step 4: Combine fragments into a unified JSON structure
    merged_json = combine_fragments_to_json(json_fragments)

    # Step 5: Save merged JSON to a file
    output_json_path = "converted_output.json"
    save_json_to_file(merged_json, output_json_path)

    # Step 6: Convert JSON to CSV
    json_to_csv(merged_json)


# Execute the script
if __name__ == "__main__":
    main()

import subprocess
import os
import time
from bs4 import BeautifulSoup
import pandas as pd


def pdf_to_html(input_file, output_dir):
    """
    Converts a PDF to HTML using the marker_single command.

    Parameters:
        input_file (str): Path to the input PDF file.
        output_dir (str): Path to the output directory.

    Returns:
        str: Path to the generated HTML file or None if conversion fails.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    output_format = "html"

    # Run the PDF-to-HTML conversion command
    command = [
        "marker_single",
        input_file,
        "--output_dir", output_dir,
        "--output_format", output_format
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"PDF successfully converted to HTML. Output directory: {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during PDF to HTML conversion: {e}")
        print(f"Error output: {e.stderr}")
        return None

    # Locate the HTML file
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    html_file_path = os.path.join(output_dir, base_name, f"{base_name}.html")

    if not os.path.exists(html_file_path):
        print(f"Expected HTML file not found: {html_file_path}")
        return None

    return html_file_path


def html_to_csv(html_file, output_dir):
    """
    Extracts tables from an HTML file and saves them as CSV files.

    Parameters:
        html_file (str): Path to the input HTML file.
        output_dir (str): Path to the output directory for CSV files.

    Returns:
        list: Paths to the saved CSV files.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    saved_csv_files = []
    try:
        with open(html_file, "r", encoding="utf-8") as html_file_obj:
            soup = BeautifulSoup(html_file_obj, "html.parser")

        # Extract tables
        tables = soup.find_all("table")
        if not tables:
            print("No tables found in the HTML file.")
            return saved_csv_files

        for idx, table in enumerate(tables):
            # Convert the HTML table to a pandas DataFrame
            df = pd.read_html(str(table))[0]
            csv_file_path = os.path.join(output_dir, f"table_{idx + 1}.csv")
            df.to_csv(csv_file_path, index=False)
            saved_csv_files.append(csv_file_path)
            print(f"Table {idx + 1} saved as CSV at: {csv_file_path}")

    except Exception as e:
        print(f"An error occurred while processing the HTML file: {e}")

    return saved_csv_files


# Example Usage with Timing
if __name__ == "__main__":
    input_pdf = "input.pdf"
    html_output_dir = "output_directory"
    csv_output_dir = os.path.join(html_output_dir, "csv_tables")

    start_time = time.time()  # Start timer

    # Convert PDF to HTML
    html_file = pdf_to_html(input_pdf, html_output_dir)

    if html_file:
        # Extract tables from HTML and save as CSV
        saved_files = html_to_csv(html_file, csv_output_dir)

        print("\nProcessed CSV files:")
        for file in saved_files:
            print(file)

    end_time = time.time()  # End timer
    total_time = end_time - start_time
    print(f"\nTotal processing time: {total_time:.2f} seconds")

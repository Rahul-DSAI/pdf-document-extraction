"""LlamaParse-based PDF parsing and JSON/CSV export utilities."""
import csv
import json
import os
import re
from pathlib import Path

import nest_asyncio
from llama_parse import LlamaParse

nest_asyncio.apply()


def initialize_parser(api_key=None, result_type="markdown", num_workers=6, language="en", verbose=True):
    api_key = api_key or os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        raise RuntimeError("Set LLAMA_CLOUD_API_KEY in your environment.")
    return LlamaParse(
        api_key=api_key,
        result_type=result_type,
        num_workers=num_workers,
        language=language,
        verbose=verbose,
        parsing_instruction=(
            "Extract tables from the PDF and preserve their structure. "
            "Represent tables in structured JSON with clear column names."
        ),
    )


def extract_markdown_text(parser, file_paths):
    docs = parser.load_data([str(p) for p in file_paths])
    return "".join(doc.text for doc in docs)


def extract_json_fragments(markdown_content):
    return re.findall(r"```json\s*(.*?)\s*```", markdown_content, re.DOTALL)


def combine_fragments_to_json(json_fragments):
    merged = {"data_sections": []}
    for fragment in json_fragments:
        try:
            merged["data_sections"].append(json.loads(fragment))
        except json.JSONDecodeError:
            continue
    return merged


def save_json_to_file(data, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def json_to_csv(data, output_dir="outputs/csv_tables"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    table_count = 0

    for section_index, section in enumerate(data.get("data_sections", []), start=1):
        candidates = []
        if isinstance(section, dict):
            for value in section.values():
                if isinstance(value, list):
                    candidates.append(value)
                elif isinstance(value, dict) and isinstance(value.get("Table"), list):
                    candidates.append(value["Table"])

        for table in candidates:
            if not table:
                continue
            if isinstance(table[0], dict):
                headers = list(table[0].keys())
                rows = [[row.get(header, "") for header in headers] for row in table]
            elif isinstance(table[0], list):
                headers = [f"Column{i + 1}" for i in range(len(table[0]))]
                rows = table
            else:
                headers = [f"Column{i + 1}" for i in range(len(table))]
                rows = [table]

            table_count += 1
            target = output_dir / f"table_{table_count}.csv"
            with target.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream)
                writer.writerow(headers)
                writer.writerows(rows)

    return table_count


def parse_pdf_to_json(pdf_path, output_path, result_type="markdown"):
    parser = initialize_parser(result_type=result_type)
    markdown = extract_markdown_text(parser, [pdf_path])
    data = combine_fragments_to_json(extract_json_fragments(markdown))
    save_json_to_file(data, output_path)
    return data

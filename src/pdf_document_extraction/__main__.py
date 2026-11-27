"""Command-line entry point for PDF table extraction."""
import argparse
from pathlib import Path
from .marker_pipeline import pdf_to_html, html_to_csv


def main():
    parser = argparse.ArgumentParser(description="Extract tables from a PDF into CSV files using Marker.")
    parser.add_argument("pdf", help="Path to the input PDF")
    parser.add_argument("--output-dir", default="outputs/marker", help="Output directory")
    args = parser.parse_args()

    html_path = pdf_to_html(args.pdf, args.output_dir)
    if not html_path:
        raise SystemExit("PDF-to-HTML conversion failed.")
    csv_dir = str(Path(args.output_dir) / "csv_tables")
    csv_files = html_to_csv(html_path, csv_dir)
    print(f"Exported {len(csv_files)} table(s) to {csv_dir}")


if __name__ == "__main__":
    main()

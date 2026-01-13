# PDF Converter

A reusable Python utility for converting PDFs to cleaned, structured Excel workbooks with automatic table extraction, consolidation, code parsing, and deduplication.

## Features

- **PDF Table Extraction**: Uses `pdfplumber` to detect and extract real table structures from PDFs (falls back to text extraction via PyPDF2).
- **Automatic Cleaning**: Detects header rows, extracts embedded dates, flattens multiline cells, and normalizes whitespace.
- **Consolidation**: Combines multiple sheets into a single, unified table.
- **Code Parsing**: Parses waste codes (or similar hierarchical codes) into Section/Subsection/Item columns.
- **Deduplication**: Removes exact and near-duplicate rows based on Code, Date, and Description.
- **Column Trimming**: Removes unnecessary columns for cleaner output.
- **Excel ↔ PDF Conversion**: Convert cleaned Excel workbooks back to PDF if needed.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/PDF_Converter.git
   cd PDF_Converter
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Example

```python
from pdf_converter import PDFConverter

# Initialize converter
pc = PDFConverter()

# Process a PDF into a cleaned Excel workbook
output_path = pc.process_pdf_to_clean_excel(
    input_pdf='path/to/your/input.pdf',
    final_output_xlsx='path/to/output_final.xlsx'
)

print(f"Output saved to: {output_path}")
```

### Pipeline Steps

The `process_pdf_to_clean_excel()` method orchestrates the following steps:

1. **Extract** — Read tables from PDF or extract text
2. **Clean** — Detect headers, extract dates, flatten cells
3. **Consolidate** — Merge multiple sheets with code/description parsing
4. **Parse Sections** — Extract hierarchical codes (section/subsection/item)
5. **Dedupe & Trim** — Remove duplicates and unnecessary columns

### Advanced Options

```python
pc.process_pdf_to_clean_excel(
    input_pdf='input.pdf',
    final_output_xlsx='output.xlsx',
    temp_raw_excel='temp_raw.xlsx',  # Optional: specify temp file location
    keep_intermediate=True             # Keep intermediate workbooks for inspection
)
```

## Testing

Run the test suite:

```bash
pytest tests/
```

Tests cover:
- Sheet cleaning and header detection
- Sheet consolidation and code extraction
- Code parsing into hierarchical levels
- Deduplication and column trimming

## Project Structure

```
PDF_Converter/
├── pdf_converter.py               # Main module with PDFConverter and PDF_to_Excel_Converter classes
├── tests/
│   └── test_pdf_converter_pipeline.py  # Unit tests for pipeline methods
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Classes

### PDFConverter

Main class providing the complete PDF → cleaned Excel pipeline.

**Key Methods:**
- `process_pdf_to_clean_excel(input_pdf, final_output_xlsx, ...)` — Full end-to-end processing
- `_clean_sheets_inplace(excel_path)` — Clean individual sheets
- `_consolidate_sheets(excel_in, excel_out)` — Merge and extract codes
- `_parse_sections_and_finalize(excel_in, excel_out)` — Parse hierarchical codes
- `_dedupe_and_trim(excel_in, excel_out)` — Remove duplicates and trim columns
- `read_excel()` / `convert_to_pdf()` — Convert Excel to PDF (legacy functionality)

### PDF_to_Excel_Converter

Utility class for initial PDF extraction.

**Key Methods:**
- `read_pdf()` — Extract tables or text from PDF
- `convert_to_excel()` — Write extracted data to Excel sheets

## Dependencies

- **pandas** — Data manipulation and Excel I/O
- **openpyxl** — Excel workbook handling
- **pdfplumber** — Table extraction from PDFs (preferred)
- **PyPDF2** — Fallback text extraction from PDFs
- **fpdf2** — PDF generation (for Excel → PDF conversion)
- **pytest** — Testing framework

## Example Workflow

```python
from pdf_converter import PDFConverter

# Create converter instance
pc = PDFConverter()

# Process a complex PDF with multiple tables
pdf_path = 'regulations.pdf'
output_path = 'regulations_clean.xlsx'

result = pc.process_pdf_to_clean_excel(pdf_path, output_path)

# Output Excel file contains:
# - Code: hierarchical code identifier
# - Section: first-level code
# - Subsection: second-level code
# - Item: third-level code
# - Date: extracted date (if present)
# - Description: item description
# - Raw: original concatenated row text
```

## Tips & Best Practices

1. **Inspect Intermediate Files**: Set `keep_intermediate=True` to examine intermediate workbooks and debug issues.
2. **Handle Edge Cases**: Some PDFs may require manual adjustment if table structure is highly irregular.
3. **Leading Zeros**: Numeric codes without leading zeros are preserved as-is; use `.zfill()` to normalize if needed.
4. **Date Formats**: The pipeline recognizes dates in `DD/MM/YYYY` or `MM-DD-YYYY` format; adjust regex in `_clean_sheets_inplace()` if your PDFs use different formats.

## License

MIT (or your preferred license)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Support

For questions or issues, please open a GitHub issue or contact the maintainer.

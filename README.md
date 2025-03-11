# PDF to Markdown Converter with Mistral OCR

A Python tool that converts PDF documents to Markdown format using Mistral's OCR API, preserving images and text formatting.

## Features

- 📝 Converts PDF files to well-formatted Markdown
- 🖼️ Extracts and saves images from PDFs
- 📋 Maintains page structure with clear separators
- 🗂️ Organized output structure with original file names
- 🔄 Automatic file management (moves processed files)
- 🎨 Color-coded terminal output for better visibility
- 🔒 Secure API key handling through environment variables

## Directory Structure

```
.
├── pdfs_to_process/    # Place PDFs here for processing
├── pdfs-done/         # Processed PDFs are moved here
└── ocr_output/        # Output directory
    └── your_pdf_name/  # One folder per PDF
        ├── your_pdf_name.md  # Markdown with same name as PDF
        ├── page1_img1.png    # Extracted images
        ├── page2_img1.png
        └── .metadata/        # Technical data
            └── ocr_response.json
```

## Requirements

- Python 3.7+
- Mistral AI API key (get one at https://console.mistral.ai/api-keys)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```bash
MISTRAL_API_KEY=your_api_key_here
```

## Usage

1. Place your PDF files in the `pdfs_to_process` directory

2. Run the converter:
```bash
python pdf_converter.py
```

3. Find the converted files in `ocr_output/`:
   - Each PDF gets its own directory named after the PDF
   - Markdown file has the same name as the PDF
   - Images are stored alongside the markdown file
   - Original PDFs are moved to `pdfs-done/`

## Output Format

The converter creates:

1. A markdown file with:
   - Title matching the PDF name
   - Page numbers and separators
   - Properly linked images
   - Original text formatting preserved

2. Extracted images:
   - Named systematically (page1_img1.png, etc.)
   - Stored alongside the markdown
   - Linked relatively in the markdown

3. Metadata:
   - Raw OCR response stored in `.metadata/`
   - JSON format for potential reprocessing

## Error Handling

- Colorized error messages
- Detailed progress logging
- Graceful failure handling
- Summary of successful/failed conversions

## Limitations

- Requires Mistral AI API key
- Processing time depends on PDF size and complexity
- API usage limits apply based on your Mistral AI plan


## Acknowledgments

- Mistral AI for the OCR API
- Python community for the excellent libraries 
- Original ipynb approach - https://github.com/diegomarzaa/pdf-ocr-obsidian/
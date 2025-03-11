import os
import json
import base64
import shutil
from pathlib import Path
from termcolor import colored
from dotenv import load_dotenv
from mistralai import Mistral, DocumentURLChunk
from mistralai.models import OCRResponse

# Constants and Configuration
INPUT_DIR = Path("pdfs_to_process")   # Folder where the user places the PDFs to be processed
DONE_DIR = Path("pdfs-done")          # Folder where processed PDFs will be moved
OUTPUT_ROOT_DIR = Path("ocr_output")   # Root folder for conversion results

def setup_environment():
    """Setup environment and initialize Mistral client"""
    try:
        load_dotenv()
        api_key = os.getenv("MISTRAL_API_KEY")
        
        if not api_key:
            print(colored("Error: MISTRAL_API_KEY not found in .env file", "red"))
            return None
            
        print(colored(f"Loaded API Key: {api_key[:4]}...", "green"))
        return Mistral(api_key=api_key)
    except Exception as e:
        print(colored(f"Error setting up environment: {str(e)}", "red"))
        return None

def setup_directories():
    """Create necessary directories if they don't exist"""
    try:
        INPUT_DIR.mkdir(exist_ok=True)
        DONE_DIR.mkdir(exist_ok=True)
        OUTPUT_ROOT_DIR.mkdir(exist_ok=True)
        print(colored("✓ Directories setup complete", "green"))
        return True
    except Exception as e:
        print(colored(f"Error setting up directories: {str(e)}", "red"))
        return False

def process_pdf(pdf_path: Path, client: Mistral):
    """Process a single PDF file"""
    try:
        # PDF base name
        pdf_base = pdf_path.stem
        print(colored(f"Processing {pdf_path.name}...", "cyan"))
        
        # Output folders - create a folder with the same name as PDF
        output_dir = OUTPUT_ROOT_DIR / pdf_base
        output_dir.mkdir(exist_ok=True)
        
        # Read PDF file
        print(colored("Reading PDF file...", "cyan"))
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        if len(pdf_bytes) == 0:
            print(colored(f"Error: PDF file {pdf_path} is empty", "red"))
            return False
            
        # Upload file to Mistral
        print(colored("Uploading to Mistral...", "cyan"))
        uploaded_file = client.files.upload(
            file={
                "file_name": pdf_path.name,
                "content": pdf_bytes,
            },
            purpose="ocr"
        )
        
        # Get signed URL and process with OCR
        print(colored("Processing with OCR...", "cyan"))
        signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
        
        ocr_response = client.ocr.process(
            document=DocumentURLChunk(document_url=signed_url.url),
            model="mistral-ocr-latest",
            include_image_base64=True
        )
        
        # Save OCR response in a metadata folder
        print(colored("Saving OCR response...", "cyan"))
        metadata_dir = output_dir / ".metadata"
        metadata_dir.mkdir(exist_ok=True)
        ocr_json_path = metadata_dir / "ocr_response.json"
        with open(ocr_json_path, "w", encoding="utf-8") as json_file:
            json.dump(ocr_response.dict(), json_file, indent=4, ensure_ascii=False)
        print(colored(f"✓ OCR response saved in {ocr_json_path}", "green"))
        
        # Process markdown and images
        print(colored("Processing markdown and images...", "cyan"))
        global_counter = 1
        updated_markdown_pages = []
        
        for page_num, page in enumerate(ocr_response.pages, 1):
            print(colored(f"Processing page {page_num}...", "cyan"))
            updated_markdown = page.markdown
            
            # Add page separator and title
            if page_num > 1:
                updated_markdown = f"\n\n---\n\n## Page {page_num}\n\n" + updated_markdown
            else:
                updated_markdown = f"# {pdf_base}\n\n## Page {page_num}\n\n" + updated_markdown
            
            for image_obj in page.images:
                try:
                    print(colored(f"Processing image {image_obj.id}...", "cyan"))
                    # Process base64 image
                    base64_str = image_obj.image_base64
                    if base64_str.startswith("data:"):
                        base64_str = base64_str.split(",", 1)[1]
                    image_bytes = base64.b64decode(base64_str)
                    
                    # Save image with a more descriptive name
                    ext = Path(image_obj.id).suffix if Path(image_obj.id).suffix else ".png"
                    new_image_name = f"page{page_num}_img{global_counter}{ext}"
                    global_counter += 1
                    
                    # Save image directly in the output directory
                    image_output_path = output_dir / new_image_name
                    with open(image_output_path, "wb") as f:
                        f.write(image_bytes)
                    
                    print(colored(f"✓ Saved image: {new_image_name}", "green"))
                    
                    # Update markdown with standard markdown image link
                    # Using relative path from the markdown file to the image
                    updated_markdown = updated_markdown.replace(
                        f"![{image_obj.id}]({image_obj.id})",
                        f"![{new_image_name}]({new_image_name})"
                    )
                except Exception as e:
                    print(colored(f"Error processing image {image_obj.id}: {str(e)}", "yellow"))
                    continue
                    
            updated_markdown_pages.append(updated_markdown)
        
        # Save final markdown with same name as PDF
        print(colored("Saving final markdown...", "cyan"))
        final_markdown = "\n\n".join(updated_markdown_pages)
        
        # Add a header with navigation info
        header = f"""# {pdf_base}

> This file was generated using Mistral OCR. Images are stored alongside this markdown file.

---

"""
        final_markdown = header + final_markdown
        
        # Save markdown with same name as PDF
        output_markdown_path = output_dir / f"{pdf_base}.md"
        with open(output_markdown_path, "w", encoding="utf-8") as md_file:
            md_file.write(final_markdown)
            
        print(colored(f"✓ Successfully processed {pdf_path.name}", "green"))
        print(colored(f"✓ Output saved to: {output_markdown_path}", "green"))
        
        # Move processed PDF to done directory
        shutil.move(str(pdf_path), DONE_DIR / pdf_path.name)
        print(colored(f"✓ {pdf_path.name} moved to {DONE_DIR}", "green"))
        
        return True
        
    except Exception as e:
        print(colored(f"Error processing {pdf_path.name}: {str(e)}", "red"))
        return False

def main():
    """Main application function"""
    print(colored("Starting PDF to Markdown converter...", "cyan"))
    
    # Setup environment and initialize Mistral client
    client = setup_environment()
    if not client:
        print(colored("Failed to setup environment. Exiting...", "red"))
        exit(1)
    
    # Setup directories
    if not setup_directories():
        print(colored("Failed to setup directories. Exiting...", "red"))
        exit(1)
    
    # Get PDF files
    pdf_files = list(INPUT_DIR.glob("*.pdf"))
    if not pdf_files:
        print(colored("No PDFs found in pdfs_to_process directory", "yellow"))
        exit(0)
    
    print(colored(f"Found {len(pdf_files)} PDF(s) to process", "cyan"))
    
    # Process each PDF
    success_count = 0
    for pdf_file in pdf_files:
        if process_pdf(pdf_file, client):
            success_count += 1
    
    # Print summary
    if success_count == len(pdf_files):
        print(colored(f"All {success_count} PDFs processed successfully!", "green"))
    else:
        print(colored(f"Processed {success_count} out of {len(pdf_files)} PDFs successfully", "yellow"))

if __name__ == "__main__":
    main() 
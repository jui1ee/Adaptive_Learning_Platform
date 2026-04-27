"""
PDF text extraction for NLP pipelines.
Extracts text with options for combined or per-page output.
Automatically manages output directories.
"""

import pdfplumber
import sys
from pathlib import Path
import re


def extract_text_from_pdf(pdf_path, as_pages=False):
    """
    Extract text from PDF. Returns combined text or per-page list.
    
    Args:
        pdf_path (str): Path to the PDF file.
        as_pages (bool): If True, return list of page texts. 
                        If False, return single combined string.
    
    Returns:
        str or list: Combined text (str) or list of page texts.
                    Returns None if extraction fails.
    """
    try:
        pages_text = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    # Clean excessive newlines
                    text = text.replace("\n", " ")
                    text = re.sub(r'\s+', ' ', text).strip()
                    pages_text.append(text)
        
        if as_pages:
            return pages_text if pages_text else []
        else:
            return "\n\n".join(pages_text) if pages_text else ""
    
    except FileNotFoundError:
        print(f"Error: PDF file '{pdf_path}' not found.")
        return None
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None


def save_text_to_file(text, output_filename, output_dir="data/processed"):
    """
    Save extracted text to a .txt file in specified directory.
    Creates directory if it doesn't exist.
    
    Args:
        text (str or list): The text to save (string or list of pages).
        output_filename (str): Filename for output (e.g., "output.txt").
        output_dir (str): Directory path (default: "data/processed").
    
    Returns:
        str: Path to saved file, or None if failed.
    """
    try:
        # Create directory if needed
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Handle both string and list input
        if isinstance(text, list):
            content = "\n\n".join(text)
        else:
            content = text
        
        file_path = output_path / output_filename
        file_path.write_text(content, encoding="utf-8")
        
        print(f"✓ Saved to {file_path}")
        return str(file_path)
    
    except Exception as e:
        print(f"Error saving file: {e}")
        return None


def pdf_to_text(pdf_path, output_filename="extracted.txt", as_pages=False, 
                output_dir="data/extracted"):
    """
    Main function: Extract PDF text and save to file.
    """
    text = extract_text_from_pdf(pdf_path, as_pages=True)  # always get pages

    if text is None:
        return None

    if not text or not any(text):
        print("Warning: No text extracted from PDF.")
        return text

    # ✅ Auto filename from PDF name
    pdf_name = Path(pdf_path).stem
    output_filename = f"{pdf_name}.txt"

    save_path = save_text_to_file(text, output_filename, output_dir)

    # ✅ Return both formats
    result = {
        "full_text": "\n\n".join(text),
        "pages": text
    }

    return result if save_path else None


# Example usage
# if __name__ == "__main__":
#     if len(sys.argv) >= 2:
#         pdf_file = sys.argv[1]
#         as_pages = "--pages" in sys.argv
#     else:
#         pdf_file = "sample.pdf"
#         as_pages = False
    
#     result = pdf_to_text(pdf_file, as_pages=as_pages)

#     print("\n--- SAMPLE OUTPUT ---")
#     print(result["full_text"][:500])  # print first 500 chars
#     sys.exit(0 if result is not None else 1)

if __name__ == "__main__":
    raw_dir = Path("data/raw")

    if not raw_dir.exists():
        print("❌ data/raw folder not found")
        sys.exit(1)

    pdf_files = list(raw_dir.glob("*.pdf"))

    if not pdf_files:
        print("⚠️ No PDF files found in data/raw/")
        sys.exit(1)

    print(f"📂 Found {len(pdf_files)} PDF(s)\n")

    for pdf_file in pdf_files:
        print(f"🔄 Processing: {pdf_file.name}")

        result = pdf_to_text(str(pdf_file))

        if result:
            print(f"✅ Done: {pdf_file.name}\n")
        else:
            print(f"❌ Failed: {pdf_file.name}\n")

    print("🎉 All files processed!")

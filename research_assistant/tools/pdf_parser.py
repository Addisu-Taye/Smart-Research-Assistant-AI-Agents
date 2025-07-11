# -*- coding: utf-8 -*-
# Developed by: Addisu Taye & Kidist Demessie
# Date: 2024-06-15
# Purpose: Extract text from PDFs
# Key Features:
#   - PyPDF2 integration
#   - Batch processing (implied, though single file here)
#   - Text normalization

from PyPDF2 import PdfReader
# Assuming utils.helpers.normalize_text exists.
# If not, you might need to provide a placeholder or implement it.
from utils.helpers import normalize_text 

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts and cleans text from a PDF file.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The extracted and normalized text content from the PDF.

    Raises:
        ValueError: If PDF extraction fails.
    """
    print(f"PDF Parser: Attempting to extract text from PDF: {file_path}")
    try:
        reader = PdfReader(file_path)
        raw_text = ""
        for page in reader.pages:
            page_content = page.extract_text()
            if page_content: # Ensure page content is not None before joining
                raw_text += page_content
        
        if not raw_text:
            print(f"PDF Parser: No text extracted from {file_path}.")
            return "" # Return empty string if no text found

        normalized_text = normalize_text(raw_text)
        print(f"PDF Parser: Successfully extracted and normalized text from {file_path}.")
        return normalized_text
    except Exception as e:
        print(f"PDF Parser: Error during PDF extraction from {file_path}: {e}")
        raise ValueError(f"PDF extraction failed: {e}")


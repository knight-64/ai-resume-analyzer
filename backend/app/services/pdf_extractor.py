"""Extract text from PDF files"""

from pypdf import PdfReader
from io import BytesIO


def extract_text_from_pdf(pdf_file_content: bytes) -> str:
    """
    Extract text from a PDF file.

    Args:
        pdf_file_content: Binary content of the PDF file

    Returns:
        Extracted text from the PDF

    Raises:
        ValueError: If PDF cannot be read or is empty
    """
    try:
        # Create a BytesIO object from the bytes
        pdf_stream = BytesIO(pdf_file_content)

        # Read the PDF
        reader = PdfReader(pdf_stream)

        if len(reader.pages) == 0:
            raise ValueError("PDF file has no pages")

        # Extract text from all pages
        text_parts = []
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text.strip():  # Only add non-empty pages
                text_parts.append(text)

        extracted_text = "\n\n".join(text_parts)

        if not extracted_text.strip():
            raise ValueError("No text could be extracted from PDF")

        return extracted_text

    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")

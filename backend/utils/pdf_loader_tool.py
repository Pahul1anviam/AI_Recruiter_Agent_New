from langchain_community.document_loaders import PyMuPDFLoader
from pdf2image import convert_from_path
import pytesseract
import os

def load_pdf_text(file_path: str) -> str:
    try:
        # Try extracting text normally using PyMuPDF
        loader = PyMuPDFLoader(file_path)
        documents = loader.load()
        content = " ".join([doc.page_content for doc in documents])
        
        if content.strip():
            return content
        else:
            print("[OCR] No text found. Running OCR...")
            return ocr_fallback(file_path)
        
    except Exception as e:
        print(f"[ERROR] PDF Load failed: {e}")
        return ocr_fallback(file_path)

def ocr_fallback(file_path: str) -> str:
    try:
        images = convert_from_path(file_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"[OCR ERROR]: {e}")
        return ""

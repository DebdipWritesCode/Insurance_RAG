import pdfplumber
from pdf2image import convert_from_path
import pytesseract

def extract_text_from_pdf(pdf_path: str) -> list[str]:
    full_text = ""
    ocr_needed_pages = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                full_text += text + "\n"
            else:
                print(f"⚠️ No text found on page {i+1} with pdfplumber, marking for OCR")
                ocr_needed_pages.append(i)

    chunks = [chunk.strip() for chunk in full_text.split("\n\n") if chunk.strip()]
    
    if ocr_needed_pages:
        print("Falling back to OCR for some pages")
        slides = convert_from_path(pdf_path, dpi=300)
        for i in ocr_needed_pages:
            image = slides[i]
            ocr_text = pytesseract.image_to_string(image)
            ocr_chunks = [chunk.strip() for chunk in ocr_text.split("\n\n") if chunk.strip()]
            chunks.extend(ocr_chunks)
    
    print(f"📄 Extracted {len(chunks)} chunks from PDF using pdfplumber")
    print(f"🔍 First chunk (100 chars): {repr(chunks[0][:100]) if chunks else 'No chunks'}")
    
    return chunks
import os
import tempfile
from pptx import Presentation
from pdf2image import convert_from_path
import pytesseract

def pptx_to_pdf(pptx_path: str, output_pdf_path: str) -> None:
    """
    Converts a PPTX file to PDF using LibreOffice (soffice).
    Works on Linux/Mac. On Windows, use PowerPoint automation instead.
    """
    command = f'soffice --headless --convert-to pdf "{pptx_path}" --outdir "{os.path.dirname(output_pdf_path)}"'
    os.system(command)
    
def extract_text_from_pdf_ocr(pdf_path: str) -> list[str]:
    slides = convert_from_path(pdf_path, dpi=300)
    all_chunks = []

    for i, image in enumerate(slides):
        print(f"🔍 OCR on slide {i+1}")
        text = pytesseract.image_to_string(image)
        chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
        all_chunks.extend(chunks)

    print(f"🖼️ Extracted {len(all_chunks)} chunks from OCR (PDF-based)")
    return all_chunks

def extract_text_from_pptx(pptx_path: str) -> list[str]:
  prs = Presentation(pptx_path)
  full_text = []
  has_text = False
  
  for i, slide in enumerate(prs.slides):
    slide_text = []
    for shape in slide.shapes:
      if hasattr(shape, "text") and shape.text.strip():
        slide_text.append(shape.text.strip())
        
    if slide_text:
      full_text.append("\n".join(slide_text))
      has_text = True
      
  if has_text:
    print("📊 Text found in PPTX. OCR not needed.")
    return [chunk.strip() for chunk in full_text if chunk.strip()]
  
  print("⚠️ No text found in any slide — falling back to PDF + OCR")
  
  with tempfile.TemporaryDirectory() as tmpdir:
    pdf_path = os.path.join(tmpdir, "converted.pdf")
    pptx_to_pdf(pptx_path, pdf_path)
    ocr_chunks = extract_text_from_pdf_ocr(pdf_path)

  print(f"📊 Extracted {len(ocr_chunks)} chunks from PPTX")
  print(f"🔍 First chunk (100 chars): {repr(ocr_chunks[0][:100]) if ocr_chunks else 'No chunks'}")

  return ocr_chunks
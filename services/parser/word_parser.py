from docx import Document

def extract_text_from_docx(docx_path: str) -> list[str]:
  doc = Document(docx_path)
  full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
  
  chunks = [chunk.strip() for chunk in full_text.split("\n\n") if chunk.strip()]
  
  print(f"📝 Extracted {len(chunks)} chunks from DOCX")
  print(f"🔍 First chunk (100 chars): {repr(chunks[0][:100]) if chunks else 'No chunks'}")

  return chunks
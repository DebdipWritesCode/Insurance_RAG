from pptx import Presentation

def extract_text_from_pptx(pptx_path: str) -> list[str]:
  prs = Presentation(pptx_path)
  full_text = []
  
  for i, slide in enumerate(prs.slides):
    slide_text = []
    for shape in slide.shapes:
      if hasattr(shape, "text"):
        slide_text.append(shape.text.strip())
        
    if slide_text:
      full_text.append("\n".join(slide_text))
    else:
      print(f"⚠️ No text found on slide {i+1}")
      
  chunks = [chunk.strip() for chunk in full_text if chunk.strip()]
  
  print(f"📊 Extracted {len(chunks)} chunks from PPTX")
  print(f"🔍 First chunk (100 chars): {repr(chunks[0][:100]) if chunks else 'No chunks'}")

  return chunks
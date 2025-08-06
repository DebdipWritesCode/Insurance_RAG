from PIL import Image
import pytesseract

def extract_text_from_image(image_path: str) -> list[str]:
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    
    print(f"🖼️ Extracted text from image: {text[:100]}...")  # Log first 100 chars for debugging

    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]

    print(f"🖼️ Extracted {len(chunks)} chunks from image")
    print(f"🔍 First chunk (100 chars): {repr(chunks[0][:100]) if chunks else 'No chunks'}")

    return chunks

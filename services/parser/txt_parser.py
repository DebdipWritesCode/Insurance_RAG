def extract_text_from_txt(txt_path: str) -> list[str]:
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]

    print(f"📜 Extracted {len(chunks)} chunks from TXT")
    print(f"🔍 First chunk (100 chars): {repr(chunks[0][:100]) if chunks else 'No chunks'}")

    return chunks

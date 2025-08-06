from openpyxl import load_workbook

def extract_text_from_xlsx(file_path: str) -> list[str]:
  wb = load_workbook(filename=file_path, read_only=True, data_only=True)
  full_text = []
  
  for sheet in wb.worksheets:
    for row in sheet.iter_rows(values_only=True):
      row_text = " | ".join([str(cell) for cell in row if cell is not None])
      if row_text.strip():
        full_text.append(row_text)
        
  chunks = [chunk.strip() for chunk in full_text if chunk.strip()]
  
  print(f"📊 Extracted {len(chunks)} chunks from Excel")
  print(f"🔍 First chunk (100 chars): {repr(chunks[0][:100]) if chunks else 'No chunks'}")

  return chunks
from fastapi import APIRouter, HTTPException
import requests
import io
from docx import Document
import os
import sys

# Add the parent directory to the path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use relative import instead of absolute import
from schemas.entry_point import EntryPointInput

router = APIRouter()


@router.post("/entry_point")
def get_transcripts(entry_point_input: EntryPointInput):
    # Download the file from the URL
    pass




gdrive_url_gemini = (
    "https://docs.google.com/feeds/download/documents/export/Export?id=1lmy55R593uDuZmS0K_yXWO3u2n3Y5OsjieCQWTw6ggU&exportFormat=txt"
)

# Extraer el texto
text_content = get_transcripts(gdrive_url_gemini, TranscriptType.GEMINI)
print(text_content)

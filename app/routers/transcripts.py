from fastapi import APIRouter, HTTPException
import requests
import io
from docx import Document
import os
import sys

# Add the parent directory to the path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use relative import instead of absolute import
from schemas.transcripts import TranscriptType

router = APIRouter()


@router.post("/get_transcripts")
def get_transcripts(url: str, transcript_type: TranscriptType):
    # Download the file from the URL
    if transcript_type == TranscriptType.TACTIQ:
        try:
            response = requests.get(url)
            response.raise_for_status()
            docx_bytes = io.BytesIO(response.content)
            doc = Document(docx_bytes)

            # Extract text from each paragraph
            transcripts = []
            for paragraph in doc.paragraphs:
                transcripts.append(paragraph.text)

            return "\n".join(transcripts)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif transcript_type == TranscriptType.GEMINI:
        try:
            response = requests.get(url)
            response.raise_for_status()
            transcript = response.text
            return transcript
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


gdrive_url = (
    "https://drive.google.com/uc?id=1kbSVkSIRz1Fh8YY6UQjhzUYNn61cj7Z7&export=download"
)

gdrive_url_gemini = (
    "https://docs.google.com/feeds/download/documents/export/Export?id=1lmy55R593uDuZmS0K_yXWO3u2n3Y5OsjieCQWTw6ggU&exportFormat=txt"
)

# Extraer el texto
text_content = get_transcripts(gdrive_url_gemini, TranscriptType.GEMINI)
print(text_content)

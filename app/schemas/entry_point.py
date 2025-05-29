from enum import Enum
from pydantic import BaseModel

class TranscriptType(str, Enum):
    TACTIQ = "tactiq"
    GEMINI = "gemini"


class EntryPointInput(BaseModel):
    transcript_type: TranscriptType
    url: str

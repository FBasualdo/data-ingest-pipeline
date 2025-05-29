from pydantic import BaseModel, Field
from typing import TypedDict, List
from enum import Enum





class MetadataOutput(BaseModel):
    id: int = Field(description="El id del segmento")
    title: str = Field(description="Un titulo para el segmento")
    summary: str = Field(description="Un pequeño resumen del contenido")
    speakers: List[str] = Field(description="Los involucrados en el segmento")
    main_topics: List[str] = Field(
        description="Los temas principales del segmento, los cuales pueden ser tomados de la lista de topics disponibles o nuevos temas"
    )


class ChunkOutput(BaseModel):
    metadata: MetadataOutput = Field(description="Los metadatos del segmento")
    content: str = Field(description="El segmento de la transcripcion original")


class ListOfChunksOutput(BaseModel):
    chunks: List[ChunkOutput] = Field(
        description="Lista de chunks de la transcripcion original creada con el agentic chunking method"
    )

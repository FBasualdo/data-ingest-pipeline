import voyageai
from typing import Union, List
import PIL
import os


class Embedder:
    def __init__(self):
        pass
    
    def create_embeddings(
        self,
        content: Union[str, List[str], PIL.Image],
        model: str = "voyage-multimodal-3",
    ):
        client = voyageai.Client()
        result = client.multimodal_embed(content, model=model)

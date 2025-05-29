import os
import anthropic
import sys
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from dotenv import load_dotenv
from typing import List
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts.transcripts_prompts import (
    ENHANCE_TRANSCRIPT_INSTRUCTIONS,
    ENHANCE_TRANSCRIPT_DESCRIPTION,
)
from schemas.transcripts import ListOfChunksOutput


load_dotenv()


class TranscriptEnhancer:
    def __init__(self):
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    def split_in_chunks_before_enhance_tactiq(
        self, transcript: str, max_chunk_size: int, overlap: int = 500
    ) -> List[str]:
        """
        Split transcript into chunks with overlap between consecutive chunks.
        Ensures chunks end at a timestamp marker to avoid cutting conversations mid-way.

        Args:
            transcript: The text to split (format: "HH:MM:SS Speaker: Text")
            max_chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks (default: 500)

        Returns:
            List of text chunks with overlap
        """
        if max_chunk_size <= overlap:
            raise ValueError("max_chunk_size must be greater than overlap")

        chunks = []
        i = 0

        while i < len(transcript):
            # Calculate the potential end position
            potential_end = min(i + max_chunk_size, len(transcript))

            # If we're at the end of the transcript, add the final chunk and break
            if potential_end == len(transcript):
                chunks.append(transcript[i:potential_end])
                break

            # Look for the next timestamp after the potential end
            # Timestamps are in format HH:MM:SS or MM:SS
            next_timestamp_pos = -1

            # Search for the next timestamp pattern within a reasonable range after potential_end
            search_end = min(potential_end + 200, len(transcript))  # Look ahead a bit
            search_text = transcript[potential_end:search_end]

            # Look for timestamp patterns like "01:00:02" or "59:27"
            import re

            timestamp_matches = re.finditer(r"\d{2}:\d{2}(?::\d{2})? ", search_text)

            for match in timestamp_matches:
                next_timestamp_pos = potential_end + match.start()
                break

            # If no timestamp found, use the original end
            if next_timestamp_pos == -1:
                end = potential_end
            else:
                end = next_timestamp_pos

            # Add the chunk
            chunks.append(transcript[i:end])

            # Move to the next position, accounting for overlap
            i = max(i, end - overlap)

            # Find the first timestamp in the overlap section
            if i > 0 and i < len(transcript):
                overlap_section = transcript[i : min(i + overlap, len(transcript))]
                timestamp_matches = re.finditer(
                    r"\d{2}:\d{2}(?::\d{2})? ", overlap_section
                )

                for match in timestamp_matches:
                    i = i + match.start()
                    break

        return chunks

    def split_in_chunks_before_enhance_gemini(
        self, transcript: str, max_chunk_size: int, overlap: int = 500
    ):
        """
        Split transcript into chunks with overlap between consecutive chunks.
        Ensures chunks end at a timestamp marker to avoid cutting conversations mid-way.
        Specifically designed for Gemini transcripts which have a specific format with
        timestamps like "00:00:00" at the beginning of speaker turns.

        Args:
            transcript: The text to split (format from Gemini: "00:00:00 Speaker: Text")
            max_chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks
        """
        # Extract just the transcription part from the Gemini document
        import re
        
        # Find the transcription section
        summary_match = re.search(r'📝 Notas.*?Registros de la reunión', transcript, re.DOTALL)

        if summary_match:
            summary_text = summary_match.group(0)
        else:
            summary_text = transcript        

        transcript_section_match = re.search(r'📖 Transcripción.*?La transcripción finalizó', 
                                            transcript, re.DOTALL)
        
        if transcript_section_match:
            transcript_text = transcript_section_match.group(0)
        else:
            # If we can't find the specific section, use the whole text
            transcript_text = transcript
            
        # Split the transcript into chunks
        chunks = []
        i = 0
        
        while i < len(transcript_text):
            # Calculate the potential end position
            potential_end = min(i + max_chunk_size, len(transcript_text))
            
            # If we're at the end of the transcript, add the final chunk and break
            if potential_end == len(transcript_text):
                chunks.append(transcript_text[i:potential_end])
                break
                
            # Look for the next timestamp after the potential end
            search_end = min(potential_end + 200, len(transcript_text))
            search_text = transcript_text[potential_end:search_end]
            
            # Look for timestamp patterns like "00:00:00"
            timestamp_matches = re.finditer(r"\d{2}:\d{2}:\d{2}", search_text)
            
            next_timestamp_pos = -1
            for match in timestamp_matches:
                next_timestamp_pos = potential_end + match.start()
                break
                
            # If no timestamp found, use the original end
            if next_timestamp_pos == -1:
                end = potential_end
            else:
                end = next_timestamp_pos
                
            # Add the chunk
            chunks.append(transcript_text[i:end])
            
            # Move to the next position, accounting for overlap
            i = max(i, end - overlap)
            
            # Find the first timestamp in the overlap section
            if i > 0 and i < len(transcript_text):
                overlap_section = transcript_text[i:min(i + overlap, len(transcript_text))]
                timestamp_matches = re.finditer(r"\d{2}:\d{2}:\d{2}", overlap_section)
                
                for match in timestamp_matches:
                    i = i + match.start()
                    break
                    
        return chunks

    def enhance_transcript(
        self,
        splitted_transcripts: List[str],
        raw_transcript: str,
        max_chunk_size: int,
        available_topics: List[str],
    ) -> dict:
        """
        Enhances transcript chunks by analyzing and organizing them into coherent segments.

        This function processes each chunk of a transcript using an AI agent to determine
        if it should be merged with previous chunks or treated as a new segment. It handles
        the continuity of ideas across chunks and ensures proper organization of the transcript.

        Args:
            splitted_transcripts (List[str]): List of transcript chunks to be processed
            raw_transcript (str): The original complete transcript text
            max_chunk_size (int): Maximum size for each chunk
            available_topics (List[str]): List of predefined topics for categorization

        Returns:
            dict: A dictionary containing the enhanced transcript chunks with metadata
                 in the format {"chunks": [enhanced_chunks]}
        """

        enhanced_transcripts = []
        last_chunk = None

        for i, chunk in enumerate(splitted_transcripts):
            last_chunk_data = "None" if i == 0 else last_chunk
            enhancer = Agent(
                model=OpenAIChat(id="gpt-4o-mini"),
                description=ENHANCE_TRANSCRIPT_DESCRIPTION.format(
                    max_chunk_size=max_chunk_size,
                    available_topics=available_topics,
                    last_chunk=last_chunk_data,
                ),
                instructions=ENHANCE_TRANSCRIPT_INSTRUCTIONS,
                response_model=ListOfChunksOutput,
            )

            print(f"Current Chunk: {chunk}")
            chunk_result = enhancer.run(message=f"Current Chunk: {chunk}")
            print(chunk_result)
            if (
                i > 0
                and chunk_result.content.chunks
                and chunk_result.content.chunks[0].metadata.id == last_chunk.metadata.id
            ):
                enhanced_transcripts[-1] = chunk_result.content.chunks[0]

                if len(chunk_result.content.chunks) > 1:
                    enhanced_transcripts.extend(chunk_result.content.chunks[1:])
            else:
                enhanced_transcripts.extend(chunk_result.content.chunks)

            last_chunk = (
                chunk_result.content.chunks[-1]
                if chunk_result.content.chunks
                else last_chunk
            )

        return {"chunks": enhanced_transcripts}

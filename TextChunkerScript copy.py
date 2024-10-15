
import re
import hashlib
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, field
import nltk
from nltk.tokenize import word_tokenize

nltk.download('punkt', quiet=True)
nltk.download('words', quiet=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@dataclass
class Chunk:
    id: int
    type: str
    content: str
    start_context: str
    end_context: str
    flags: Dict[str, bool] = field(default_factory=lambda: {"overlap": False, "missing": False})
    version: int = 1
    hash: str = field(init=False)

    def __post_init__(self):
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        return hashlib.md5(self.content.encode()).hexdigest()

    def update_content(self, new_content: str):
        self.content = new_content
        self.version += 1
        self.hash = self.calculate_hash()

class VersionControl:
    def __init__(self):
        self.chunk_versions: Dict[int, List[Chunk]] = {}

    def add_chunk_version(self, chunk: Chunk):
        if chunk.id not in self.chunk_versions:
            self.chunk_versions[chunk.id] = []
        self.chunk_versions[chunk.id].append(chunk)

    def get_latest_version(self, chunk_id: int) -> Optional[Chunk]:
        if chunk_id in self.chunk_versions and self.chunk_versions[chunk_id]:
            return max(self.chunk_versions[chunk_id], key=lambda c: c.version)
        return None

    def get_version_history(self, chunk_id: int) -> List[Chunk]:
        return self.chunk_versions.get(chunk_id, [])

class TextChunker:
    def __init__(self, max_chunk_size: int = 1000, overlap_size: int = 50):
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.chunk_id = 0

    def chunk_text(self, text: str) -> List[Chunk]:
        chunks = []
        paragraphs = self._split_paragraphs(text)
        
        for paragraph in paragraphs:
            if len(paragraph) <= self.max_chunk_size:
                chunks.append(self._create_chunk(paragraph, "paragraph"))
            else:
                chunks.extend(self._split_large_paragraph(paragraph))
        
        self._add_context_markers(chunks)
        return chunks

    def _split_paragraphs(self, text: str) -> List[str]:
        return re.split(r'\n\s*\n', text.strip())

    def _split_large_paragraph(self, paragraph: str) -> List[Chunk]:
        words = word_tokenize(paragraph)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= self.max_chunk_size:
                current_chunk.append(word)
                current_length += len(word) + 1
            else:
                chunks.append(self._create_chunk(' '.join(current_chunk), "sentence"))

                current_chunk = current_chunk[-self.overlap_size:] + [word] 
                current_length = sum(len(w) + 1 for w in current_chunk) - 1
        
        if current_chunk:
            chunks.append(self._create_chunk(' '.join(current_chunk), "sentence"))
        
        return chunks

    def _create_chunk(self, content: str, chunk_type: str) -> Chunk:
        self.chunk_id += 1
        return Chunk(
            id=self.chunk_id,
            type=chunk_type,
            content=content,
            start_context="",
            end_context=""
        )

    def _add_context_markers(self, chunks: List[Chunk]):
        for i, chunk in enumerate(chunks):
            if i > 0:
                chunk.start_context = ' '.join(word_tokenize(chunks[i-1].content)[-self.overlap_size:])
            if i < len(chunks) - 1:
                chunk.end_context = ' '.join(word_tokenize(chunks[i+1].content)[:self.overlap_size])

# Additional classes and methods will continue from here
# Ensure proper handling of code blocks, special entities, managing versions, and GUI elements for text processing 

class VersionControl:
    def __init__(self):
        self.chunk_versions: Dict[int, List[Chunk]] = {}

    def add_chunk_version(self, chunk: Chunk):
        if chunk.id not in self.chunk_versions:
            self.chunk_versions[chunk.id] = []
        self.chunk_versions[chunk.id].append(chunk)

    def get_latest_version(self, chunk_id: int) -> Optional[Chunk]:
        if chunk_id in self.chunk_versions and self.chunk_versions[chunk_id]:
            return max(self.chunk_versions[chunk_id], key=lambda c: c.version)
        return None

    def get_version_history(self, chunk_id: int) -> List[Chunk]:
        return self.chunk_versions.get(chunk_id, [])

class ChunkService:
    """Service for splitting text into chunks."""

    def create_chunks(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> list[str]:
        chunks = []

        start = 0

        while start < len(text):
            end = start + chunk_size

            chunks.append(text[start:end])

            start += chunk_size - chunk_overlap

        return chunks
"""Create local vector representations for questions and PDF passages."""

from pathlib import Path
from typing import Protocol, Sequence

DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class EmbeddingModel(Protocol):
    """Small interface that keeps retrieval independent from one model library."""

    def embed_query(self, text: str) -> list[float]: ...

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...


class LocalEmbeddingModel:
    """Generate multilingual embeddings locally with FastEmbed and ONNX."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        cache_dir: str | Path = ".cache/fastembed",
    ) -> None:
        self.model_name = model_name
        self.cache_dir = str(cache_dir)
        self._model = None

    @property
    def model(self):
        """Load the model only when the first embedding is requested."""
        if self._model is None:
            from fastembed import TextEmbedding

            self._model = TextEmbedding(
                model_name=self.model_name,
                cache_dir=self.cache_dir,
            )
        return self._model

    def embed_query(self, text: str) -> list[float]:
        vector = next(iter(self.model.query_embed(text)))
        return vector.tolist()

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self.model.passage_embed(texts)]

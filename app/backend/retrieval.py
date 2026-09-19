"""
retrieval.py — Knowledge base retrieval for AgriSense Edge.

Embeds crop-disease notes with a small multilingual model and stores
vectors in SQLite. Retrieves top-k entries by disease label first,
then by semantic similarity to the farmer's question.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.backend.db import Database


@dataclass
class RetrievalResult:
    """A single retrieved knowledge base entry."""

    crop: str
    disease: str
    text: str
    source_file: str
    similarity: float


class RetrievalEngine:
    """Knowledge base retrieval engine with embedding-based search."""

    def __init__(self, db: Database, embedding_model_dir: str | Path | None = None):
        self._db = db
        self._model_dir = (
            Path(embedding_model_dir) if embedding_model_dir else Path("models/embeddings")
        )
        self._model = None
        self._loaded = False

    def load(self) -> None:
        """Load the embedding model."""
        # TODO: Load all-MiniLM-L6-v2 ONNX model
        self._loaded = True
        print("RetrievalEngine loaded")

    def unload(self) -> None:
        """Release embedding model resources."""
        self._model = None
        self._loaded = False

    def embed_text(self, text: str) -> np.ndarray:
        """Compute embedding for a text string.

        Args:
            text: Input text (Hindi or English).

        Returns:
            Embedding vector as numpy array.
        """
        # TODO: Implement actual embedding
        # Stub: return zero vector
        return np.zeros(384, dtype=np.float32)

    def retrieve(
        self,
        disease_label: str | None = None,
        question: str | None = None,
        top_k: int = 3,
    ) -> list[RetrievalResult]:
        """Retrieve relevant knowledge base entries.

        Strategy:
        1. If disease_label is provided, filter by disease first.
        2. If question is provided, rank by embedding similarity.
        3. Return top_k results.

        Args:
            disease_label: Disease classification result (e.g., "Tomato___Early_blight").
            question: Farmer's question in Hindi.
            top_k: Number of results to return.

        Returns:
            List of RetrievalResult sorted by relevance.
        """
        # Parse disease label
        crop = None
        disease = None
        if disease_label and "___" in disease_label:
            parts = disease_label.split("___", 1)
            crop = parts[0]
            disease = parts[1] if len(parts) > 1 else None

        # Get candidates from DB
        rows = self._db.get_kb_vectors(crop=crop, disease=disease)

        if not rows:
            # Broaden search — try just by crop, or all entries
            rows = self._db.get_kb_vectors(crop=crop)
            if not rows:
                rows = self._db.get_kb_vectors()

        # If no question, return by label match only
        if not question or not self._loaded:
            results = [
                RetrievalResult(
                    crop=row["crop"],
                    disease=row["disease"],
                    text=row["chunk_text"],
                    source_file=row["source_file"],
                    similarity=1.0 if crop and row["crop"] == crop else 0.5,
                )
                for row in rows
            ]
            return sorted(results, key=lambda r: -r.similarity)[:top_k]

        # Semantic ranking
        query_embedding = self.embed_text(question)
        results = []
        for row in rows:
            if row["embedding"]:
                doc_embedding = np.frombuffer(row["embedding"], dtype=np.float32)
                similarity = float(self._cosine_similarity(query_embedding, doc_embedding))
            else:
                similarity = 0.0

            results.append(
                RetrievalResult(
                    crop=row["crop"],
                    disease=row["disease"],
                    text=row["chunk_text"],
                    source_file=row["source_file"],
                    similarity=similarity,
                )
            )

        return sorted(results, key=lambda r: -r.similarity)[:top_k]

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def index_knowledge_base(self, kb_dir: str | Path) -> int:
        """Index all knowledge base files into the database.

        Reads markdown files from kb_dir, embeds them, and stores in SQLite.

        Args:
            kb_dir: Path to knowledge base directory.

        Returns:
            Number of entries indexed.
        """
        kb_path = Path(kb_dir)
        count = 0

        for md_file in sorted(kb_path.glob("*.md")):
            # Parse filename: crop_disease.md
            stem = md_file.stem
            parts = stem.split("_", 1)
            crop = parts[0] if parts else "unknown"
            disease = parts[1] if len(parts) > 1 else "general"

            text = md_file.read_text(encoding="utf-8")
            embedding = self.embed_text(text)

            self._db.save_kb_vector(
                source_file=md_file.name,
                crop=crop,
                disease=disease,
                chunk_text=text,
                embedding=embedding.tobytes(),
            )
            count += 1

        return count

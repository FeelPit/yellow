from typing import Optional


class VectorService:
    """ChromaDB-backed vector storage for messages and profile matching."""

    def __init__(self):
        try:
            import chromadb
            self.client = chromadb.Client()
            self._available = True
        except Exception:
            self._available = False

    def _get_collection(self, name: str):
        if not self._available:
            return None
        return self.client.get_or_create_collection(name=name)

    # --- Message storage (per session) ---

    def store_message(self, session_id: str, message_id: str, content: str, role: str):
        collection = self._get_collection(f"session_{session_id.replace('-', '')}")
        if not collection:
            return
        try:
            collection.add(
                documents=[content],
                ids=[message_id],
                metadatas=[{"role": role}],
            )
        except Exception:
            pass

    def get_relevant_context(self, session_id: str, query: str, n_results: int = 5) -> list[str]:
        collection = self._get_collection(f"session_{session_id.replace('-', '')}")
        if not collection or collection.count() == 0:
            return []
        try:
            results = collection.query(
                query_texts=[query],
                n_results=min(n_results, collection.count()),
                where={"role": "user"},
            )
            return results["documents"][0] if results["documents"] else []
        except Exception:
            return []

    # --- Profile matching (global collection) ---

    def upsert_profile_embedding(self, user_id: str, profile_text: str):
        """Store or update a user's profile as an embedding for matching."""
        collection = self._get_collection("profiles")
        if not collection:
            return
        try:
            collection.upsert(
                documents=[profile_text],
                ids=[user_id],
            )
        except Exception:
            pass

    def find_similar_profiles(self, user_id: str, profile_text: str, n_results: int = 10) -> list[tuple[str, float]]:
        """Find most similar profiles. Returns list of (user_id, distance)."""
        collection = self._get_collection("profiles")
        if not collection or collection.count() < 2:
            return []
        try:
            results = collection.query(
                query_texts=[profile_text],
                n_results=min(n_results + 1, collection.count()),
            )
            pairs = []
            if results["ids"] and results["distances"]:
                for uid, dist in zip(results["ids"][0], results["distances"][0]):
                    if uid != user_id:
                        pairs.append((uid, dist))
            return pairs[:n_results]
        except Exception:
            return []


class MockVectorService:
    """Mock vector service for testing — no-op storage, simple text matching fallback."""

    def store_message(self, session_id: str, message_id: str, content: str, role: str):
        pass

    def get_relevant_context(self, session_id: str, query: str, n_results: int = 5) -> list[str]:
        return []

    def upsert_profile_embedding(self, user_id: str, profile_text: str):
        pass

    def find_similar_profiles(self, user_id: str, profile_text: str, n_results: int = 10) -> list[tuple[str, float]]:
        return []

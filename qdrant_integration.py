from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np

class QdrantSwarm:
    def __init__(self, collection_name: str, vector_size: int = 768):
        self.client = QdrantClient("localhost", port=6333)
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self._create_collection()

    def _create_collection(self):
        """Create a new collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        if self.collection_name not in [c.name for c in collections]:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )

    def add_texts(self, texts: List[str], metadata: List[Dict] = None):
        """
        Add texts to the vector database.

        Args:
            texts (List[str]): List of texts to add to the database.
            metadata (List[Dict], optional): List of metadata dictionaries corresponding to each text.

        Returns:
            None
        """
        vectors = self.model.encode(texts)
        points = []
        for i, (text, vector) in enumerate(zip(texts, vectors)):
            point = PointStruct(
                id=i,
                vector=vector.tolist(),
                payload={"text": text, **(metadata[i] if metadata else {})}
            )
            points.append(point)
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar texts in the vector database.

        Args:
            query (str): The query text to search for.
            top_k (int): The number of top results to return.

        Returns:
            List[Dict]: A list of dictionaries containing the search results.
        """
        query_vector = self.model.encode(query)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector.tolist(),
            limit=top_k
        )
        return [{"text": r.payload["text"], "score": r.score, **r.payload} for r in results]

    def delete_texts(self, ids: List[int]):
        """
        Delete texts from the vector database.

        Args:
            ids (List[int]): List of IDs of the texts to delete.

        Returns:
            None
        """
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    Filter.ids(ids)
                ]
            )
        )

    def get_collection_info(self):
        """
        Get information about the collection.

        Returns:
            Dict: Information about the collection.
        """
        return self.client.get_collection(self.collection_name)

# Example usage:
if __name__ == "__main__":
    qdrant_swarm = QdrantSwarm("test_collection")
    
    # Add some texts
    texts = [
        "The quick brown fox jumps over the lazy dog",
        "Python is a versatile programming language",
        "Machine learning is transforming various industries"
    ]
    qdrant_swarm.add_texts(texts)
    
    # Search for similar texts
    query = "Programming languages"
    results = qdrant_swarm.search(query)
    print(f"Search results for '{query}':")
    for r in results:
        print(f"Text: {r['text']}, Score: {r['score']}")
    
    # Get collection info
    info = qdrant_swarm.get_collection_info()
    print(f"\nCollection info: {info}")
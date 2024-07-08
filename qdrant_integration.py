from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter
from sentence_transformers import SentenceTransformer
from typing import List, Dict


class QdrantSwarm:
    """
    A class to interact with Qdrant vector database for storing and retrieving text embeddings.
    """

    def __init__(self, collection_name: str):
        """
        Initialize the QdrantSwarm instance.

        Args:
            collection_name (str): Name of the Qdrant collection to use.
        """
        self.client = QdrantClient("localhost", port=6333)
        self.collection_name = collection_name
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_size = self.model.get_sentence_embedding_dimension()
        self._create_collection()

    def _create_collection(self):
        """
        Create a new collection in Qdrant if it doesn't already exist.
        """
        collections = self.client.get_collections().collections
        if self.collection_name not in [c.name for c in collections]:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
            )

    def encode_text(self, text: str) -> List[float]:
        """
        Encode the input text into a vector embedding.

        Args:
            text (str): The text to encode.

        Returns:
            List[float]: The vector embedding of the input text.
        """
        return self.model.encode(text).tolist()

    def add_texts(self, texts: List[str], metadata: List[Dict] = None):
        """
        Add multiple texts and their metadata to the Qdrant collection.

        Args:
            texts (List[str]): List of texts to add.
            metadata (List[Dict], optional): List of metadata dictionaries corresponding to each text.
        """
        vectors = [self.encode_text(text) for text in texts]
        points = []
        for i, (text, vector) in enumerate(zip(texts, vectors)):
            point = PointStruct(
                id=i,
                vector=vector,
                payload={"text": text, **(metadata[i] if metadata else {})}
            )
            points.append(point)
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar texts in the Qdrant collection.

        Args:
            query (str): The query text to search for.
            top_k (int): The number of top results to return.

        Returns:
            List[Dict]: A list of dictionaries containing the search results.
        """
        query_vector = self.encode_text(query)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
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
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams



class QdrantRepository:
    def __init__(self, collection_name: str, distance_method = Distance.COSINE):
        self.collection_name = collection_name
        self.distance_method = distance_method
        self.client = QdrantClient(host="localhost", port=6333)

    def store(self, vectors: list, ids: list, payloads: list):
        """
        Store vectors and payloads in Qdrant collection.
        Args:
            vectors (list): List of vectors to store.
            payloads (list): List of payloads associated with the vectors.

        Returns:
            List of ids of the stored points.
        """
        self.client.upload_collection(
          collection_name = self.collection_name,
          vectors=vectors,
          ids=ids,
          payload=payloads,
        )

    def search(self, vector: list, limit: int = 1, filter: dict = None):
        """
        Search in the collection using the given vector.
        Args:
            vector (list): Vector to search with.
            limit (int): Number of results to return.
            filter (dict): Additional filter to apply to the search results.

        Returns:
            List of search results.
        """
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
        )

        return search_result
    
    def create_collection(self, vector_size: int = 512):
        if (self.collection_name in self.client.get_collections()):
            return
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=vector_size, distance=self.distance_method),
        )
    
    
if __name__ == "__main__":
    repository = QdrantRepository("faces")
    repository.create_collection(512)

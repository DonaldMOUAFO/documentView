import faiss
import numpy as np

from src.infrastructure import config

def build_hnsw_index(
        embeddings: np.ndarray, 
        m: int = 32, 
        ef_construction: int = 128,
        ef_search: int = 64
    ):
    """
    Build a FAISS HNSW index from the given embeddings.
    Args:
        embeddings (np.ndarray): A 2D array of embeddings with the shape (num_samples, embedding_dim).
            Must be normalized if using IndexHNSWFlat for cosine similarity.
        m (int): The number of neighbors in the HNSW graph (default: 16).
        ef_construction (int): The size of the dynamic list for construction (default: 200).
        ef_search (int): The size of the dynamic list for search (default: 64).
    
    Returns:
        faiss.IndexHNSWFlat: A FAISS HNSW index containing the provided embeddings.
    """
    dim = embeddings.shape[1]
    index = faiss.IndexHNSWFlat(
        dim, m, faiss.METRIC_INNER_PRODUCT
    )  # Inner Product = cosine similarity with normalized vectors

    index.hnsw.efConstruction = ef_construction
    index.hnsw.efSearch = ef_search
    index.add(embeddings.astype(np.float32))
    
    return index

def save_index(index, index_path=config.INDEX_FILE_PATH):
    faiss.write_index(index, str(index_path))
    print(f"FAISS index saved to {index_path}...")

def load_index(index_path=config.INDEX_FILE_PATH):
    if not index_path.exists():
        raise FileNotFoundError(f"FAISS index file not found: {index_path}")   
    return faiss.read_index(str(index_path))
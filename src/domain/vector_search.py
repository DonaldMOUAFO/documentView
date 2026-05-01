import faiss
import numpy as np
from os import path
import streamlit as st

from src.infrastructure import config
from src.interface.streamlit_app import inform_message

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

def save_index(index, index_file_path): 
    faiss.write_index(
        index, str(index_file_path)
    )
    inform_message(f"FAISS index saved to {index_file_path}...")

def load_index(index_path=config.INDEX_FILE_PATH):
    indexes = faiss.read_index(str(index_path))
    inform_message(
        f"mbeddings successfully saved at {index_path}..."
    )  
    return indexes
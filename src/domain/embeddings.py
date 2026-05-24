import json
import numpy as np
from typing import Dict
from sentence_transformers import SentenceTransformer
from src.infrastructure import config
from src.interface.streamlit_utils import inform_message

def load_model(model_name: str) -> SentenceTransformer:
    """
    Load a pre-trained SentenceTransformer model.
    Args:
        model_name (str): The name of the pre-trained model to load.
    Returns:
        SentenceTransformer: The loaded SentenceTransformer model.
    """
    try:
        model = SentenceTransformer(model_name)
        return model
    except Exception as e:
        print(f"Error loading model '{model_name}': {e}")
        raise

def compute_embeddings(
        chunks, model=None, 
        batch_size: int = 16, normalize: bool = True
    ):

    if model is None: 
        model = SentenceTransformer(config.EMBEDINGS_MODEL_NAME) 
    
    if isinstance(chunks, list) :
        embeddings = model.encode(
            chunks,
            batch_size=batch_size,
            normalize_embeddings=normalize,
            convert_to_numpy=True,
            show_progress_bar=True,
        )
    else :
        embeddings = model.encode(
            chunks, normalize_embeddings=normalize, convert_to_numpy=True
        )
        return embeddings

    if normalize:
        try :
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            embeddings = embeddings / norms 
        except Exception as e :
            # st.error(f" Error reading Pdf : {e}\nMake you document fulfill the requirements")
            embeddings = None
    return embeddings

def save_embeddings(embeddings, embs_file_path):
    np.save(embs_file_path, embeddings)
    inform_message(
        f"Embeddings successfully saved at:\n{embs_file_path}..."
    )

def save_meta_data(metadata, metadata_file_path=config.META_DATA_FILE_PATH):
    json.dump(metadata, open(metadata_file_path, "w", encoding="utf-8"), indent=2)
    print(f"metadata successfully saved at {metadata_file_path}")

def load_embeddings(emb_file_path=config.EMBEDINGS_FILE_PATH):
    embeddings = np.load(emb_file_path)
    return embeddings

def compute_cosine_similarity(vec, matrix):
    return matrix @ vec 

def top_k_similar(query_emb, emb_matrix, texts, metadata, 
        k=config.DEFAULT_TOP_K, sim_threshold=0.1) -> list[Dict[str, any]]:
    
    sims = compute_cosine_similarity(query_emb, emb_matrix)
    ranked = np.argsort(-sims)
    
    results = []
    for idx in ranked[:k*2]: # consider more thant k to allow for threshold ffiltering
        score = float(sims[idx])

        if score < sim_threshold and len(results) >= k:
            break

        results.append({
            "id": metadata[idx]["id"],
            "text": texts[idx],
            "score": score,
            "topic": metadata[idx].get("topics", "unknown")
        })

        if len(results) >= k:
            break

    #idx = np.argpartition(-sims, k)[:k]
    #idx = idx[np.argsort(-sims[idx])]
    #return #idx, sims[idx]

    return results
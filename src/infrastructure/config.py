import streamlit as st
from os import getenv
from pathlib import Path

BASE_DIR = Path(getenv("DATA_DIR", Path.cwd() / "data"))
BASE_DIR.mkdir(parents=True, exist_ok=True)

CORPUS_DIR = BASE_DIR / "corpus"
OUTPUT_DIR = BASE_DIR / "output"
INDEXES_DIR = BASE_DIR / "indexes"
EMBEDINGS_DIR = BASE_DIR / "embeddings"

for d in [CORPUS_DIR, OUTPUT_DIR, INDEXES_DIR, EMBEDINGS_DIR]:
    # Create the directory if it doesn't exist
    # The parents=True argument allows the creation of parent directories if they don't exist,
    # and exist_ok=True prevents an error if the directory already exists.
    d.mkdir(parents=True, exist_ok=True)

CORPUS_FILE_PATH = CORPUS_DIR / "corpus.txt"
EMBEDINGS_FILE_PATH = EMBEDINGS_DIR / "embeddings.npy"
META_DATA_FILE_PATH = EMBEDINGS_DIR / "meta_data.json"
INDEX_FILE_PATH = EMBEDINGS_DIR / "faiss_hnsw.index"

#EMBEDINGS_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDINGS_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

DEFAULT_TOP_K = 5
SIM_THRESHOLD = 0.35 # not used in this lesson, but fine to keep

OLLAMA_BASE_URL = getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_API_URL  = f"{OLLAMA_BASE_URL}/api/generate"
OLLAME_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"

FILE_CONFIG = {
    "index": (INDEXES_DIR, ".index"),
    "emb": (EMBEDINGS_DIR, ".npy"),
    "corpus": (CORPUS_DIR, ".json"),
}

def prepare_file_path(file_name: str, file_type: str = "emb"):
    try:
        base_dir, suffix = FILE_CONFIG[file_type]
    except KeyError:
        raise ValueError(f"Unknown file_type: {file_type}")
    
    return Path(base_dir) / f"{Path(file_name).stem}{suffix}"       
import streamlit as st
from os import path, getenv, makedirs

PRESENT_DIR = path.dirname(path.realpath(__file__)) 

CORPUS_DIR = path.join(PRESENT_DIR, "../../data/corpus")
OUTPUT_DIR = path.join(PRESENT_DIR, "../../data/output")
INDEXES_DIR =  path.join(PRESENT_DIR, "../../data/indexes")
EMBEDINGS_DIR = path.join(PRESENT_DIR, "../../data/embedings")

CORPUS_FILE_PATH = path.join(PRESENT_DIR, "../../data/corpus/corpus.txt")
EMBEDINGS_FILE_PATH = path.join(EMBEDINGS_DIR, "embeddings.npy")
META_DATA_FILE_PATH = path.join(EMBEDINGS_DIR, "meta_data.json")

INDEX_FILE_PATH = path.join(EMBEDINGS_DIR, "faiss_hnsw.index")

#EMBEDINGS_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDINGS_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

DEFAULT_TOP_K = 5
SIM_THRESHOLD = 0.35 # not used in this lesson, but fine to keep

OLLAMA_BASE_URL = getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_API_URL = f"{OLLAMA_BASE_URL}/api/generate"
OLLAME_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"

for dir in [ CORPUS_DIR, OUTPUT_DIR, INDEXES_DIR, EMBEDINGS_DIR ] :
    if not path.isdir(dir):
        makedirs(dir)

def prepare_file_path(file_name, object="emb"):
    root, _ = path.splitext(file_name) 
    if object == "index":
        file_name = root + ".index"
        return path.join(INDEXES_DIR, file_name)
    elif object == "emb" :
        file_name = root + "emb.npy"
        return path.join(EMBEDINGS_DIR, file_name)
    elif object == "corpus" :
        file_name = root + "corpus.json"
        return path.join(CORPUS_DIR, file_name)
    else :
        st.error(
            st.error(f"The object {object} does not correspond to any of the list ['emb', 'index', 'corpus']")
        )
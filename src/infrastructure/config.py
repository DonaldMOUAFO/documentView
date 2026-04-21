from os import path, getenv

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
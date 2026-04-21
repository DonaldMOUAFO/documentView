import re
import json
from os import path
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
from src.infrastructure import config

def load_txt(file_path=config.CORPUS_FILE_PATH):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)  # normalize newlines
    text = re.sub(r'Page \d+', '', text)
    text = re.sub(r'<.*?>', '', text)  # remove HTML
    text = re.sub(r'[^\w\s.,!?()-]', '', text)
    text = text.replace("\t", " ")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, chunk_size=500, overlap=80):
    # Split text into chunks of max_length characters 
    return [text[i:i+chunk_size] for i in range(0, len(text.split()), chunk_size - overlap)]

def recursive_chunk(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200, chunk_overlap=40,
        length_function=len,
        is_separator_regex=True,
    )
    chunked_text = text_splitter.split_text(text)
    return chunked_text

def tokentextsplitter_chunk(text):
    text_splitter = TokenTextSplitter(chunk_size=50, chunk_overlap=10)
    chunked_text = text_splitter.split_text(text)
    return chunked_text

def prepare_corpus(chunked_text, file_path=config.CORPUS_FILE_PATH, meta_path=config.META_DATA_FILE_PATH):

    # texts = load_txt(file_path=file_path)
    # texts = clean_text(texts)

    # chunked_text = chunk_text(texts)

    if path.isfile(meta_path) :
        metadata = json.load(open(meta_path, "r", encoding="utf-8"))
    else:
        metadata = []

    if len(metadata) != len(chunked_text):
        metadata = [
            {"id": f"p{idx:02d}", 
             "topic": "unknown", 
             "tokens_est": len(t.split())} for idx, t in enumerate(chunked_text)
        ]

    return chunked_text, metadata 

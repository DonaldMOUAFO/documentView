import argparse
from src.infrastructure import config, prompt_engineering
from src.domain.document_handler import (load_txt, clean_text, chunk_text, 
                                         recursive_chunk, tokentextsplitter_chunk, 
                                         prepare_corpus)
from src.domain.embeddings import load_model, compute_embeddings, top_k_similar

def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d", "--document", type=str, required=False, 
        default=config.CORPUS_FILE_PATH,
        dest="doc_path",
        help="Provide the image path to locate parking place on"               
    )

    return parser.parse_args()

def rag_answer(file_path=config.CORPUS_FILE_PATH) :
    
    text = load_txt(file_path)
    text = clean_text(text)

    print("============================= CHUNK TEXT FROM chunk_text ==================================")
    chunked_text = chunk_text(text)
    print(f"len:{len(chunked_text)}\n{chunked_text}")

    print("====================================== CHUNK TEXT FROM chunked_text =======================================")
    chunked_recursive_text = recursive_chunk(text)
    print(f"len : {len(chunked_recursive_text)}\n{chunked_recursive_text}")

    print("===================================== CHUNK From tokentextsplitter_chunk TEXT =====================================")
    chunked_tokentextsplitter_text = tokentextsplitter_chunk(text)
    print(f"len : {len(chunked_tokentextsplitter_text)}\n{chunked_tokentextsplitter_text}")

    model = load_model(config.EMBEDINGS_MODEL_NAME)

    chunked_text = chunked_recursive_text
    #embeddings = compute_embeddings(chunks=chunked_text, model=model)
    embeddings = compute_embeddings(chunks=chunked_text, model=model)

    print(embeddings.shape)

    #question = "Who is Professor Kyoji Sassa ?"
    question = "What happened in Cholima and when ?"
    q_emb = compute_embeddings(chunks=question, model=model) 
    
    # print(f'Question embedding : {q_emb.shape}, embeddings : {embeddings.shape}')
    # top_k = top_k_similar(q_emb, embeddings, text, k=config.DEFAULT_TOP_K)
    # print(f"top_k : {top_k}")

    chunked_text, metadata = prepare_corpus(chunked_text, file_path=config.CORPUS_FILE_PATH, meta_path=config.META_DATA_FILE_PATH)
    
    print(f'Question embedding : {q_emb.shape}, embeddings : {embeddings.shape}, metada len : {len(metadata)}, text len : {len(chunked_text)}')
    top_k = top_k_similar(q_emb, embeddings, chunked_text, metadata, k=config.DEFAULT_TOP_K)
    print(f"===========================================TOP K ANSWER =========================================================")
    print(f"top_k : {top_k}")
    print(f"=================================================================================================================")

    prompt = prompt_engineering.build_prompt([r["text"] for r in top_k], question, allow_synthesis=True) #allow_synthesis )
    # print(f"============================================ PROMPT =============================================================================")
    # print(f"prompt: {prompt}")
    # print(f"==================================================================================================================================")

    answer_generated = prompt_engineering.rag_response_generation(
        prompt, top_k, metadata, embeddings, model,
    )
    prompt = prompt + answer_generated["answer"]
    
    return prompt
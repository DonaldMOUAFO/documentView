import re
import numpy as np
import ollama
import requests
from src.infrastructure import config

STRICT_SYSTEM_PROMPT = (
    "You are a concise assistant. Use ONLY the provided context."
    "If the answer is not contained verbatim or explicitly, say you do not know."
)

SYNTHESIZING_SYSTEM_PROMPT = (
    "You are a concise assistant. Rely ONLY on the provided context, but you MAY synthesize "
    "an answer by combining or paraphrasing the facts present. If the context truly lacks "
    "sufficient evidence, say you do not know instead of guessing."
)

USER_QUESTION_TEMPLATE = "User Question: {question}\nAnswer: "

CONTEXT_HEADER = "Context:"

def build_prompt(context, question:str, allow_synthesis: bool=False) -> str:
    
    system_prompt = SYNTHESIZING_SYSTEM_PROMPT if allow_synthesis else STRICT_SYSTEM_PROMPT
    context_str = "\n\n".join(context)

    return f"""System : {system_prompt}\n{CONTEXT_HEADER}\n{context_str}\n\n{USER_QUESTION_TEMPLATE.format(question=question)}"""

def ollama_available() -> bool:
    try:
        response = requests.get(config.OLLAME_TAGS_URL, timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False
    
def call_ollama(model:str, prompt:str, stream:bool=False)-> str:
    """Calls the Ollama API using python client if available else raw HTTP."""
    if ollama is not None :
        try:
            if stream:
                out = []
                for chunk in ollama.generate(
                    model=model, prompt=prompt, stream=True): # max_tokens=max_tokens, temperature=temperature,
                    out.append(chunk.get("response", ""))
                return "".join(out)
            else:
                resp = ollama.generate(model=model, prompt=prompt) # max_tokens=max_tokens, temperature=temperature,
                return resp.get("response", "")
        except Exception:
            pass  # Fall back to HTTP if client call fails

def _sentence_split(text:str) -> list[str] :
    """Splits text into sentences using regrex"""
    raw = re.split(r'(?<=[.!?])\s+|\n+', text.strip())
    return [s.strip() for s in raw if s and not s.isspace()]

def _compute_support(sentences, retrieved, metadata, embeddings, model):
    """Computes support scores for each sentence based on similarity to retrieved chunks."""
    # For simplicity, we can compute a relevance score for each sentence by comparing it to the retrieved chunks.
    # In a real implementation, you might want to use a more sophisticated method (e.g., cross-encoder).
    id_to_idx = {m["id"]: i for i, m in enumerate(metadata)}
    chunk_vecs, ranks = [], []
    for rank, r in enumerate(retrieved, start=1):
        idx = id_to_idx.get(r["id"])
        if idx is None:
            continue
        chunk_vecs.append(embeddings[idx])
        ranks.append(rank)
    if not chunk_vecs:
        return [], sentences  # No retrieved chunks, so no support
    chunk_vecs = np.array(chunk_vecs)
    sentence_vecs = model.encode(sentences, normalize_embeddings=True, convert_to_numpy=True)
    sims = sentence_vecs @ chunk_vecs.T
    support_scores = sims.max(axis=1)  # Take max similarity to any retrieved chunk
    return support_scores, sentences

def _apply_style(answer, style, cited_sentences):
    """Applies a style to the answer, optionally citing supporting sentences."""
    if style == "bullets" and cited_sentences:
        return "\n" + "\n".join(f"- {s}" for s in cited_sentences)
    return answer


def rag_response_generation(
        prompt, top_k_text, metadata, embeddings, model, 
        style="paragraph", llm_model_name="llama3"):
    
    #if any(pat in q_lower for pat in SYNTHESIZING_SYSTEM_PROMPT) :
    allow_synthesis = False
    heuristic_synthesis = True

    if not ollama_available():
        raise RuntimeError("Ollama is not available. Please ensure Ollama is running and accessible.")
    else :
        answer = call_ollama(model=llm_model_name, prompt=prompt) 

    # sentences = _sentence_split(answer)
    # support_rows, cited_sentences = _compute_support(
    #     sentences, top_k_text, metadata, embeddings, model
    # )
    # answer = _apply_style(answer, style, cited_sentences)
    # print("===========================================================================================================================================")
    # print(
    #     f"""answer:{answer}\nretrieved:{cited_sentences}\nsynthesis_used:{allow_synthesis}\nsynthesis_heuristic:{allow_synthesis}\nrows:{support_rows}\n
    #     "retrieved top": {top_k_text}.
    # """
    # )
    print("============================================================================================================================================")

    return {
        "answer" : answer,
        #"retrieved": top_k_text, # update cited_sentences
        #"synthesis_used" : allow_synthesis,
        #"synthesis_heuristic": allow_synthesis,
        #"rows" : support_rows,
    }
    
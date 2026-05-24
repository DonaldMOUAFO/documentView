import re
import numpy as np
import ollama
import requests
from htbuilder import div, pre, b, span
from src.infrastructure import config

STRICT_SYSTEM_PROMPT = (
    "You are a concise assistant. Use ONLY the provided context. "
    "If the answer is not contained verbatim or explicitly, say you do not know."
)

SYNTHESIZING_SYSTEM_PROMPT = (
    "You are a concise assistant. Rely ONLY on the provided context, but you MAY synthesize "
    "an answer by combining or paraphrasing the facts present. If the context truly lacks "
    "sufficient evidence, say you do not know instead of guessing."
)

USER_QUESTION_TEMPLATE = "User: {question}"
CONTEXT_HEADER = "Context"

def build_prompt(context, question:str, allow_synthesis: bool=False) -> str:
    
    system_prompt = SYNTHESIZING_SYSTEM_PROMPT if allow_synthesis else STRICT_SYSTEM_PROMPT
    context_str = "\n\n".join(context)

    return {
        "System" : system_prompt,
        "Context": context_str,
        "User": question,
    }

def history_aware_prompt(prompt, messages_historic, last_question):

    # prompt_str = f"""System:{prompt["System"]}\n\nContext:\n{prompt["Context"]}\n\nUser:{prompt["User"]}"""

    history = "\n".join(
        [f"{m['role']}:{m['content']}" for m in messages_historic]
    )

    prompt = f"""{prompt},
    
    Conversation :
    {history}

    Question :
    {last_question}
    """
    return prompt


def handle_html_content(prompt:dict):

    return div(

        b("System"),
        pre(prompt["System"]),
        tyle="display:inline-block; margin:0; vertical-align:top;"
    
        #row("System:", prompt["System"]),
        # b("System"), pre( prompt["System"] ) ,
        # div( b("Context:"), pre("".join(prompt["Context"])) ),
        # div( b("User:"), pre("".join(prompt["User"]))) ,
        # div( b("Answer:"), pre("".join(prompt["Answer"])) )
    )  

def row(label, content):
    return div(
        b(label),
        pre(content),
        tyle="display:inline-block; margin:0; vertical-align:top;"
    )  

def build_prompt_ui(prompt:dict):

    return div(
        row("System:", prompt["System"]),
        row("Context:", prompt["Context"]),
        row("User:", prompt["User"]),
        row("Answer:", prompt["Answer"])
    )

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

def generation_chat_response(model:str, prompt):
    res = ollama.chat(
        model = model,
        messages = [{"role":"user", "content":prompt}]
    )
    # {"model":"llama3",
    #  "created_at":"2026-04-27T10:32:05.764087178Z",
    #  "done":true,
    #  "done_reason":"stop",
    #  "total_duration":2923788565,
    #  "load_duration":1856887344,
    #  "prompt_eval_count":473,
    #  "prompt_eval_duration":349000694,
    #  "eval_count":39,
    #  "eval_duration":660751043,
    #  "message":"""Message(
   	#     role='assistant', 
   	#     content='Based on the provided context, [...] answer to the question.', 
   	#     thinking=None, images=None, tool_name=None, tool_calls=None
    #   )""",
    #  "logprobs":null
    # }
    #prompt["Answer"] = res["message"]["content"]
    return res["message"]["content"]

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
        prompt_str = f"""System:{prompt["System"]}\n\nContext:\n{prompt["Context"]}\n\nUser:{prompt["User"]}"""
        answer = call_ollama(model=llm_model_name, prompt=prompt_str) 

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

    prompt["Answer"] = answer

    return prompt
    # {
    #     "answer" : answer,
    #     #"retrieved": top_k_text, # update cited_sentences
    #     #"synthesis_used" : allow_synthesis,
    #     #"synthesis_heuristic": allow_synthesis,
    #     #"rows" : support_rows,
    # }
    
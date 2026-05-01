# prompt.py
def build_prompt(context, question, allow_synthesis=True):
    system_prompt = (
        "You are a concise assistant. Rely ONLY on the provided context."
        if allow_synthesis else
        "You are a concise assistant. Use ONLY the provided context."
    )

    context_str = "\n\n".join(context)

    return f"""System:{system_prompt}

Context:
{context_str}

User Question: {question}

Answer:"""
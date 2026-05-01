# memory.py
import ollama

class MemoryManager:
    def __init__(self, model="llama3", max_messages=12):
        self.model = model
        self.max_messages = max_messages
        self.messages = []
        self.summary = None

    def add_user(self, content):
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, content):
        self.messages.append({"role": "assistant", "content": content})

    def maybe_summarize(self):
        if len(self.messages) > self.max_messages:
            text = "\n".join([m["content"] for m in self.messages])

            response = ollama.generate(
                model=self.model,
                prompt=f"Summarize this conversation briefly:\n\n{text}"
            )

            self.summary = response["response"]
            self.messages = []  # reset after summarizing

    def get_context(self):
        context = []
        if self.summary:
            context.append(f"Conversation summary: {self.summary}")
        context.extend([m["content"] for m in self.messages])
        return context
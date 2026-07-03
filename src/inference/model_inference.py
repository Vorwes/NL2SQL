from llama_cpp import Llama


class LLM:
    """
    Class to handle loading and interacting with a language model for generating SQL queries based on a given database schema and user question.
    """

    def __init__(
        self, model_path: str, chat_format: str = "chatml", context_window: int = 4096
    ):
        self.model_path = model_path
        self.chat_format = chat_format
        self.context_window = context_window
        self.llm = None
        self.DDL = {
            "drop",
            "delete",
            "insert",
            "update",
            "alter",
            "create",
            "truncate",
            "grant",
            "revoke",
        }

    def load(self):
        """
        Loads The language model from the specified path with the provided chat format and context window. If the model is already loaded, it does nothing.
        """
        if self.llm is not None:
            return

        self.llm = Llama(
            model_path=self.model_path,
            chat_format=self.chat_format,
            n_ctx=self.context_window,
            verbose=False,
        )

    def generate(self, schema: str, question: str, max_tokens: int = 256):
        """
        Genrates SQL queries based on the provided database schema and user question. It streams the generated content token by token.
        """
        if self.llm is None:
            raise ValueError("Model is not loaded. Call load() before generating.")

        messages = [
            {
                "role": "system",
                "content": "You are a helpful database assistant. Your task is to generate correct SQL queries based on the provided database schema and user question.",
            },
            {
                "role": "user",
                "content": f"Here is a database schema:\n{schema}\n\nQuestion: {question}",
            },
        ]

        response_stream = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        )

        output = ""

        try:
            for chunk in response_stream:
                delta = chunk["choices"][0]["delta"]
                content = delta.get("content")
                if content:
                    output += content.lower()
                    if any(ddl_word in output for ddl_word in self.DDL):
                        yield " Sorry, I cannot generate any DDL instructions."
                        return
                    yield content
        finally:
            if ";" not in output:
                yield ";"

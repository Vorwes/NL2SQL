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

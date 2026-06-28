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

class InContextError(Exception):
    pass


class InContextUnsupportedLanguageError(InContextError):
    def __init__(self, language: str, provider: str):
        super().__init__(f"Language {language} is not supported by provider {provider}")

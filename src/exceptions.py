class InContextError(Exception):
    pass


class InContextUnsupportedLanguageError(InContextError):
    def __init__(self, language: str, provider: str):
        super().__init__(f"Language {language} is not supported by provider {provider}")


class InContextFetchError(InContextError):
    def __init__(self, base_exc: InContextError, provider: str):
        self.__cause__ = base_exc
        self.provider = provider
        super().__init__()

    def __str__(self) -> str:
        return str(self.__cause__)

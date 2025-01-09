class TokenCalculator:

    @staticmethod
    def nb_chars_to_nb_tokens(nb_chars: int) -> int:
        return nb_chars // 4

    @staticmethod
    def nb_tokens_to_nb_chars(nb_tokens: int) -> int:
        return nb_tokens * 4

    @staticmethod
    def nb_words_to_nb_tokens(nb_words: int) -> int:
        return 100 * nb_words // 75

    @staticmethod
    def nb_tokens_to_nb_words(nb_tokens: int) -> int:
        return nb_tokens * 75 // 100

    @staticmethod
    def nb_tokens_in_text_chunk(text_chunk: str) -> int:
        nb_chars = len(text_chunk)
        return TokenCalculator.nb_chars_to_nb_tokens(nb_chars)

    @staticmethod
    def optimize_chunk_size(max_tokens_input: int) -> int:
        return TokenCalculator.nb_tokens_to_nb_chars(max_tokens_input)

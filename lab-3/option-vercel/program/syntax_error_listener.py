from antlr4.error.ErrorListener import ErrorListener


class SyntaxErrorListener(ErrorListener):
    """Collect lexer and parser diagnostics without printing duplicates."""

    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(
        self, recognizer, offending_symbol, line, column, message, exception
    ):
        self.errors.append(f"line {line}:{column} {message}")

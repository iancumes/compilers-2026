from antlr4.error.ErrorListener import ErrorListener


class SyntaxErrorListener(ErrorListener):
  def __init__(self):
    super().__init__()
    self.errors = []

  def syntaxError(
    self, recognizer, offendingSymbol, line, column, msg, exception
  ):
    self.errors.append(f"line {line}:{column} {msg}")

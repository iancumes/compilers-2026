import sys
from pathlib import Path

from antlr4 import CommonTokenStream, FileStream
from antlr4.error.ErrorListener import ErrorListener
from MiniLangLexer import MiniLangLexer
from MiniLangParser import MiniLangParser


class SyntaxErrorListener(ErrorListener):
    """Collect syntax errors emitted by the lexer or parser."""

    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"linea {line}:{column} {msg}")


def parse_file(file_path):
    """Parse *file_path* and return every lexical or syntactic error."""
    error_listener = SyntaxErrorListener()
    input_stream = FileStream(str(file_path), encoding="utf-8")
    lexer = MiniLangLexer(input_stream)

    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)

    stream = CommonTokenStream(lexer)
    parser = MiniLangParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)
    parser.prog()

    return error_listener.errors


def main(argv):
    if len(argv) != 2:
        print(f"Uso: python3 {Path(argv[0]).name} <archivo>", file=sys.stderr)
        return 2

    file_path = Path(argv[1])
    if not file_path.is_file():
        print(f"Error: no se encontro el archivo '{file_path}'.", file=sys.stderr)
        return 2

    errors = parse_file(file_path)
    if errors:
        print(f"Analisis fallido: se encontraron {len(errors)} error(es).", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Analisis exitoso: '{file_path}' es sintacticamente valido.")
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))

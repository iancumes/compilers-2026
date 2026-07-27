import sys
from antlr4 import *
from SimpleLangLexer import SimpleLangLexer
from SimpleLangParser import SimpleLangParser
from syntax_error_listener import SyntaxErrorListener
from type_check_listener import TypeCheckListener
from antlr4.tree.Tree import ParseTreeWalker


def main(argv):
  if len(argv) != 2:
    print(f"Usage: python3 {argv[0]} <input-file>")
    return 1

  input_stream = FileStream(argv[1], encoding="utf-8")
  lexer = SimpleLangLexer(input_stream)
  syntax_listener = SyntaxErrorListener()
  lexer.removeErrorListeners()
  lexer.addErrorListener(syntax_listener)
  stream = CommonTokenStream(lexer)
  parser = SimpleLangParser(stream)
  parser.removeErrorListeners()
  parser.addErrorListener(syntax_listener)
  tree = parser.prog()

  if syntax_listener.errors:
    for error in syntax_listener.errors:
      print(f"Syntax error: {error}")
    print("Syntax checking failed")
    return 1

  walker = ParseTreeWalker()
  listener = TypeCheckListener()
  walker.walk(listener, tree)

  if listener.errors:
    for error in listener.errors:
      print(f"Type checking error: {error}")
    return 1

  print("Type checking passed")
  return 0


if __name__ == "__main__":
  sys.exit(main(sys.argv))

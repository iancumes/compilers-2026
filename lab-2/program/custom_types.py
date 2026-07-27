class Type:
  pass


class IntType(Type):
  def __str__(self):
    return "int"


class FloatType(Type):
  def __str__(self):
    return "float"


class StringType(Type):
  def __str__(self):
    return "string"


class BoolType(Type):
  def __str__(self):
    return "bool"


class ErrorType(Type):
  """Type used to prevent cascading errors in the listener."""

  def __str__(self):
    return "error"

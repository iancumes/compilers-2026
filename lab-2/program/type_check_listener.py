from SimpleLangListener import SimpleLangListener
from SimpleLangParser import SimpleLangParser
from custom_types import IntType, FloatType, StringType, BoolType, ErrorType


class TypeCheckListener(SimpleLangListener):
  def __init__(self):
    self.errors = []
    self.types = {}

  def exitMulDivMod(self, ctx: SimpleLangParser.MulDivModContext):
    left_type = self.types[ctx.expr(0)]
    right_type = self.types[ctx.expr(1)]

    if self.has_error_type(left_type, right_type):
      self.types[ctx] = ErrorType()
    elif ctx.op.text == "%":
      if isinstance(left_type, IntType) and isinstance(right_type, IntType):
        self.types[ctx] = IntType()
      else:
        self.errors.append(
          f"Operator % requires int operands, got {left_type} and {right_type}"
        )
        self.types[ctx] = ErrorType()
    elif self.is_numeric(left_type) and self.is_numeric(right_type):
      self.types[ctx] = self.numeric_result(left_type, right_type)
    else:
      self.errors.append(
        f"Operator {ctx.op.text} requires numeric operands, got {left_type} and {right_type}"
      )
      self.types[ctx] = ErrorType()

  def exitAddSub(self, ctx: SimpleLangParser.AddSubContext):
    left_type = self.types[ctx.expr(0)]
    right_type = self.types[ctx.expr(1)]

    if self.has_error_type(left_type, right_type):
      self.types[ctx] = ErrorType()
    elif self.is_numeric(left_type) and self.is_numeric(right_type):
      self.types[ctx] = self.numeric_result(left_type, right_type)
    else:
      self.errors.append(
        f"Operator {ctx.op.text} requires numeric operands, got {left_type} and {right_type}"
      )
      self.types[ctx] = ErrorType()

  def exitEquality(self, ctx: SimpleLangParser.EqualityContext):
    left_type = self.types[ctx.expr(0)]
    right_type = self.types[ctx.expr(1)]

    if self.has_error_type(left_type, right_type):
      self.types[ctx] = ErrorType()
    elif type(left_type) is type(right_type) or (
      self.is_numeric(left_type) and self.is_numeric(right_type)
    ):
      self.types[ctx] = BoolType()
    else:
      self.errors.append(
        f"Operator == requires compatible operands, got {left_type} and {right_type}"
      )
      self.types[ctx] = ErrorType()

  def enterInt(self, ctx: SimpleLangParser.IntContext):
    self.types[ctx] = IntType()

  def enterFloat(self, ctx: SimpleLangParser.FloatContext):
    self.types[ctx] = FloatType()

  def enterString(self, ctx: SimpleLangParser.StringContext):
    self.types[ctx] = StringType()

  def enterBool(self, ctx: SimpleLangParser.BoolContext):
    self.types[ctx] = BoolType()

  def exitParens(self, ctx: SimpleLangParser.ParensContext):
    self.types[ctx] = self.types[ctx.expr()]

  @staticmethod
  def is_numeric(value_type):
    return isinstance(value_type, (IntType, FloatType))

  @staticmethod
  def has_error_type(left_type, right_type):
    return isinstance(left_type, ErrorType) or isinstance(right_type, ErrorType)

  @staticmethod
  def numeric_result(left_type, right_type):
    if isinstance(left_type, FloatType) or isinstance(right_type, FloatType):
      return FloatType()
    return IntType()

from SimpleLangParser import SimpleLangParser
from SimpleLangVisitor import SimpleLangVisitor
from custom_types import IntType, FloatType, StringType, BoolType


class TypeCheckVisitor(SimpleLangVisitor):

  def __init__(self):
    self.errors = []

  def visitProg(self, ctx: SimpleLangParser.ProgContext):
    # A visitor normally stops when an exception is raised. Catch each
    # statement independently so every top-level type error is reported.
    for statement in ctx.stat():
      try:
        self.visit(statement)
      except TypeError as error:
        self.errors.append(str(error))

  def visitMulDivMod(self, ctx: SimpleLangParser.MulDivModContext):
    left_type = self.visit(ctx.expr(0))
    right_type = self.visit(ctx.expr(1))

    if ctx.op.text == "%":
      if isinstance(left_type, IntType) and isinstance(right_type, IntType):
        return IntType()
      raise TypeError(
        f"Operator % requires int operands, got {left_type} and {right_type}"
      )

    if isinstance(left_type, (IntType, FloatType)) and isinstance(right_type, (IntType, FloatType)):
      return FloatType() if isinstance(left_type, FloatType) or isinstance(right_type, FloatType) else IntType()
    raise TypeError(
      f"Operator {ctx.op.text} requires numeric operands, got {left_type} and {right_type}"
    )

  def visitAddSub(self, ctx: SimpleLangParser.AddSubContext):
    left_type = self.visit(ctx.expr(0))
    right_type = self.visit(ctx.expr(1))

    if isinstance(left_type, (IntType, FloatType)) and isinstance(right_type, (IntType, FloatType)):
      return FloatType() if isinstance(left_type, FloatType) or isinstance(right_type, FloatType) else IntType()
    raise TypeError(
      f"Operator {ctx.op.text} requires numeric operands, got {left_type} and {right_type}"
    )

  def visitEquality(self, ctx: SimpleLangParser.EqualityContext):
    left_type = self.visit(ctx.expr(0))
    right_type = self.visit(ctx.expr(1))

    same_type = type(left_type) is type(right_type)
    both_numeric = isinstance(left_type, (IntType, FloatType)) and isinstance(
      right_type, (IntType, FloatType)
    )
    if same_type or both_numeric:
      return BoolType()
    raise TypeError(
      f"Operator == requires compatible operands, got {left_type} and {right_type}"
    )

  def visitInt(self, ctx: SimpleLangParser.IntContext):
    return IntType()

  def visitFloat(self, ctx: SimpleLangParser.FloatContext):
    return FloatType()

  def visitString(self, ctx: SimpleLangParser.StringContext):
    return StringType()

  def visitBool(self, ctx: SimpleLangParser.BoolContext):
    return BoolType()

  def visitParens(self, ctx: SimpleLangParser.ParensContext):
    return self.visit(ctx.expr())

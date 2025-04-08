from functools import singledispatch  # noqa D100


class Expression:
    """."""

    def __init__(self, *args):
        """."""
        self.operands = tuple([
            (t if isinstance(t, Expression) else Number(t)) for t in args
        ])

    def __add__(self, other):
        """."""
        return Add(self, other)

    def __radd__(self, other):
        """."""
        return Add(other, self)

    def __sub__(self, other):
        """."""
        return Sub(self, other)

    def __rsub__(self, other):
        """."""
        return Sub(other, self)

    def __mul__(self, other):
        """."""
        return Mul(self, other)

    def __rmul__(self, other):
        """."""
        return Mul(other, self)

    def __truediv__(self, other):
        """."""
        return Div(self, other)

    def __rtruediv__(self, other):
        """."""
        return Div(other, self)

    def __pow__(self, other):
        """."""
        return Pow(self, other)

    def __rpow__(self, other):
        """."""
        return Pow(other, self)


class Operator(Expression):
    """."""

    def __repr__(self):
        """."""
        return type(self).__name__ + repr(self.operands)

    def __str__(self):
        """."""
        left = self.operands[0].__str__()
        right = self.operands[1].__str__()
        if type(self).left_precedence > type(self.operands[0]).left_precedence:
            left = "(" + left + ")"
        if type(self).left_precedence > type(self.operands[1]).right_precedence: # noqa #104
            right = "(" + right + ")"
        return left + " " + type(self).symbol + " " + right


class Add(Operator):
    """."""

    symbol = "+"
    left_precedence = 1
    right_precedence = 1


class Sub(Operator):
    """."""

    symbol = "-"
    left_precedence = 0
    right_precedence = 1


class Mul(Operator):
    """."""

    symbol = "*"
    left_precedence = 3
    right_precedence = 3


class Div(Operator):
    """."""

    symbol = "/"
    left_precedence = 2
    right_precedence = 3


class Pow(Operator):
    """."""

    symbol = "^"
    left_precedence = 4
    right_precedence = 4


class Terminal(Expression):
    """."""

    left_precedence = 100
    right_precedence = 100

    def __init__(self, value):
        """."""
        self.value = value
        self.operands = tuple()

    def __repr__(self):
        """."""
        return repr(self.value)

    def __str__(self):
        """."""
        return str(self.value)


class Number(Terminal):
    """."""

    pass


class Symbol(Terminal):
    """."""

    pass


def postvisitor(expr, fn, **kwargs):
    """."""
    stack = [expr]  # contains expressions remains to evaluate
    evaluation = {}
    while stack:
        flag = False
        last = stack[-1]
        for child in last.operands:
            if child not in evaluation.keys():
                flag = True
                stack.append(child)
        if not flag:
            evaluation[last] = fn(
                last, *(evaluation[child] for child in last.operands), **kwargs
            )
            stack = stack[0:-1]
    return evaluation[expr]


@singledispatch
def differentiate(expr, *subans, **kwargs):
    """."""
    raise NotImplementedError


@differentiate.register(Number)
def _(expr, *subans, **kwargs):
    return 0


@differentiate.register(Symbol)
def _(expr, *subans, var, **kwargs):
    return 1 if var == expr.value else 0


@differentiate.register(Add)
def _(expr, *subans, **kwargs):
    return subans[0] + subans[1]


@differentiate.register(Sub)
def _(expr, *subans, **kwargs):
    return subans[0] - subans[1]


@differentiate.register(Mul)
def _(expr, *subans, **kwargs):
    return subans[0]*expr.operands[1] + subans[1]*expr.operands[0]


@differentiate.register(Div)
def _(expr, *subans, **kwargs):
    # return subans[0] / expr.operands[1] - expr.operands[0] * subans[1]**(-2)
    return (subans[0] * expr.operands[1] - subans[1] * expr.operands[0])\
          / (expr.operands[1] ** 2)


@differentiate.register(Pow)
def _(expr, *subans, **kwargs):
    return subans[0]*expr.operands[1]*expr.operands[0]**(expr.operands[1] - 1)

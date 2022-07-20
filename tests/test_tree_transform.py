import pytest
from dataclasses import dataclass
from functools import wraps
from gcgen.api.tree import *
from typing import Any


@dataclass
class Default:
    obj: Any


@dataclass
class A:
    elems: list


@dataclass
class AA:
    elems: list


@dataclass
class B:
    label: str


@dataclass
class BB:
    label: str


@dataclass
class C:
    label: str


@dataclass
class CC:
    label: str


def ex1():
    return A(elems=[B("b1"), A(elems=[B("b_1"), C("c_1")]), C("c1"), B("b2")])


@pytest.mark.parametrize(
    "tree",
    [
        B("b1"),
        C("c1"),
        ex1(),
    ],
)
def test_transform_minimal(tree):
    """
    Test that a minimal transformer always invokes `transform_default` which
    always raises NotImplementedError.
    """

    class TransformMinimal(NodeTransformer):
        ...

    t = TransformMinimal()
    with pytest.raises(NotImplementedError):
        t.transform(tree)


@pytest.mark.parametrize(
    "tree",
    [
        B("b1"),
        C("c1"),
        ex1(),
    ],
)
def test_transform_minimal_noop_default(tree):
    """
    Test that if we implement a NOOP transformer, all trees can be traversed
    without error.
    """

    class Transformer(NodeTransformer):
        def transform_default(self, node: Any) -> Any:
            return node

    t = Transformer()
    t.transform(tree)


def test_traverse_full():
    """
    Test tree traversal involving specific and default/fallback transform
    methods.
    """

    class Transformer(NodeTransformer):
        def transform_default(self, node: Any):
            return Default(node)

        @on_transform(A)
        def transform_a(self, node: A) -> Any:
            return AA(elems=[self.transform(e) for e in node.elems])

        @on_transform(B)
        def transform_b(self, node: B) -> Any:
            return BB(label=node.label)

        @on_transform(C)
        def transform_c(self, node: C) -> Any:
            return CC(label=node.label)

    t = Transformer()
    tree = ex1()

    @dataclass
    class D:
        label: str

    tree.elems.append(D("d1"))

    def _transform_elems(e):
        if isinstance(e, A):
            return AA(elems=[_transform_elems(e) for e in e.elems])
        elif isinstance(e, B):
            return BB(e.label)
        elif isinstance(e, C):
            return CC(e.label)
        else:
            return Default(e)

    expected = _transform_elems(tree)
    assert t.transform(tree) == expected


def test_traverse_full_inheritance():
    """
    Test traversal involving specific and default transform methods using
    inheritance to expand on the base implementation.
    """

    class TransformerBase(NodeTransformer):
        def transform_default(self, node: Any):
            return Default(node)

        @on_transform(B)
        def transform_b(self, node: B) -> Any:
            return BB(label=node.label)

        @on_transform(C)
        def transform_c(self, node: C) -> Any:
            return CC(label=node.label)

    class Transformer(TransformerBase):
        @on_transform(A)
        def transform_a(self, node: A) -> Any:
            return AA(elems=[self.transform(e) for e in node.elems])

    tree = ex1()

    tb = TransformerBase()
    assert tb.transform(tree) == Default(tree)
    assert tb.transform(B("b1")) == BB("b1")

    t = Transformer()

    @dataclass
    class D:
        label: str

    tree.elems.append(D("d1"))

    def _transform_elems(e):
        if isinstance(e, A):
            return AA(elems=[_transform_elems(e) for e in e.elems])
        elif isinstance(e, B):
            return BB(e.label)
        elif isinstance(e, C):
            return CC(e.label)
        else:
            return Default(e)

    expected = _transform_elems(tree)
    assert t.transform(tree) == expected


def test_traverse_full_inheritance_override():
    """
    Test that transformer can override a handler from the base transformer
    and that the base transformer remains unaffected.
    """

    class TransformerBase(NodeTransformer):
        def transform_default(self, node: Any):
            return Default(node)

        @on_transform(A)
        def transform_a(self, node: A) -> Any:
            return AA(elems=[self.transform(e) for e in node.elems])

        @on_transform(B)
        def transform_b(self, node: B) -> Any:
            return BB(label=node.label)

        @on_transform(C)
        def transform_c(self, node: C) -> Any:
            return CC(label=node.label)

    class Transformer(TransformerBase):
        @on_transform(B)
        def transform_b(self, node: B) -> Any:
            return BB(label=node.label + "!")

    tree = ex1()

    t = Transformer()

    @dataclass
    class D:
        label: str

    tree.elems.append(D("d1"))

    def _transform_elems(e):
        if isinstance(e, A):
            return AA(elems=[_transform_elems(e) for e in e.elems])
        elif isinstance(e, B):
            return BB(e.label + "!")
        elif isinstance(e, C):
            return CC(e.label)
        else:
            return Default(e)

    expected = _transform_elems(tree)
    assert t.transform(tree) == expected


def test_traverse_handle_multi_1():
    """
    Test ability to assign one handler to handle two or more node types.
    (Giving multiple arguments to the same decorator)
    """

    @dataclass
    class BC:
        obj: object

    class Transformer(NodeTransformer):
        @on_transform(A)
        def transform_a(self, node: A) -> Any:
            return AA(elems=[self.transform(e) for e in node.elems])

        @on_transform(B, C)
        def transform_b(self, node) -> Any:
            return BC(obj=node)

    t = Transformer()

    def _transform_elems(e):
        if isinstance(e, A):
            return AA(elems=[_transform_elems(e) for e in e.elems])
        elif isinstance(e, (B, C)):
            return BC(e)
        else:
            return Default(e)

    tree = ex1()
    expected = _transform_elems(tree)
    assert t.transform(tree) == expected


def test_traverse_handle_multi_2():
    """
    Test ability to assign one handler to handle two or more node types.
    (Giving multiple arguments using multiple decorators)
    """

    @dataclass
    class BC:
        obj: object

    class Transformer(NodeTransformer):
        @on_transform(A)
        def transform_a(self, node: A) -> Any:
            return AA(elems=[self.transform(e) for e in node.elems])

        @on_transform(C)
        @on_transform(B)
        def transform_b(self, node) -> Any:
            return BC(obj=node)

    t = Transformer()

    def _transform_elems(e):
        if isinstance(e, A):
            return AA(elems=[_transform_elems(e) for e in e.elems])
        elif isinstance(e, (B, C)):
            return BC(e)
        else:
            return Default(e)

    tree = ex1()
    expected = _transform_elems(tree)
    assert t.transform(tree) == expected


def test_transform_method_override():
    """
    Transformer handlers must be given unique method names. Otherwise, if multiple
    methods are defined using the same name, only the last method defined is
    retained.
    """

    class Transformer(NodeTransformer):
        def transform_default(self, node: Any):
            return Default(node)

        @on_transform(B)
        def transform_b(self, node) -> Any:
            return BB(node.label)

        @on_transform(C)
        def transform_b(self, node) -> Any:
            return CC(node.label)

    def _transform_elems(e):
        if isinstance(e, B):
            return Default(e)
        elif isinstance(e, C):
            return CC(e.label)
        else:
            return Default(e)

    tree = ex1()
    t = Transformer()
    expected = _transform_elems(tree)
    assert t.transform(tree) == expected


def test_transform_handler_must_match_exact_type():
    """
    Test that handlers only match on *exact* types.
    """

    @dataclass
    class B2(B):
        label: str

    class Transformer(NodeTransformer):
        def transform_default(self, node: Any):
            return Default(node)

        @on_transform(B)
        def transform_b(self, node) -> Any:
            return BB(node.label)

    t = Transformer()
    assert t.transform(B("b1")) == BB("b1")
    assert t.transform(B2("b1")) == Default(B2("b1"))


def test_transform_handler_cannot_be_wrapped():
    """
    Test documenting that handlers cannot be wrapped further by other decorators
    without breaking the logic which detects and wires up handlers.

    This is not ideal behavior, but the test documents actual behavior and a
    drawback of the implementation.
    """

    def some_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

        return wrapper

    class Transformer(NodeTransformer):
        def transform_default(self, node: Any) -> Any:
            return node

        @some_decorator
        @on_visit(B)
        def visit_b(self, node: B):
            return BB(node.label)

    t = Transformer()
    assert t.transform(B("b1")) == B("b1")

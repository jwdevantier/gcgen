import pytest
from dataclasses import dataclass
from functools import wraps
from gcgen.api.tree import *
from typing import Any


@dataclass
class A:
    elems: list


@dataclass
class B:
    label: str


@dataclass
class C:
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
def test_visit_minimal(tree):
    """
    Test that a minimal visitor always invokes `visit_default` which always
    raises NotImplementedError.
    """

    class VisitMinimal(NodeVisitor):
        ...

    v = VisitMinimal()
    with pytest.raises(NotImplementedError):
        v.visit(tree)


@pytest.mark.parametrize(
    "tree",
    [
        B("b1"),
        C("c1"),
        ex1(),
    ],
)
def test_visit_minimal_noop_default(tree):
    """
    Test that if we implement a NOOP visitor, all trees can be traversed
    without error.
    """

    class VisitMinimal(NodeVisitor):
        def visit_default(self, node: Any) -> None:
            pass

    v = VisitMinimal()
    v.visit(tree)


def test_visit_full():
    """
    Test tree traversal involving specific and default/fallback visit methods.
    """

    class Visitor(NodeVisitor):
        def __init__(self):
            self.visits = []

        def visit_default(self, node: Any) -> None:
            self.visits.append(("default", node))

        @on_visit(A)
        def visit_a(self, node: A) -> None:
            self.visits.append(("va", node))
            for elem in node.elems:
                self.visit(elem)

        @on_visit(B)
        def visit_b(self, node: B) -> None:
            self.visits.append(("vb", node))

        @on_visit(C)
        def visit_c(self, node: C) -> None:
            self.visits.append(("vc", node))

    v = Visitor()
    tree = ex1()

    @dataclass
    class D:
        label: str

    tree.elems.append(D("d1"))
    v.visit(tree)
    expected_visits = []

    def visit_elem(e):
        if isinstance(e, A):
            yield "va", e
            for elem in e.elems:
                yield from visit_elem(elem)
        elif isinstance(e, B):
            yield "vb", e
        elif isinstance(e, C):
            yield "vc", e
        else:
            yield "default", e

    for entry in visit_elem(tree):
        expected_visits.append(entry)

    assert v.visits == expected_visits


def test_visit_full_inheritance():
    """
    Test traversal involving specific and default visit methods using
    inheritance to expand on the base implementation.
    """

    class VisitorBase(NodeVisitor):
        def __init__(self):
            self.visits = []

        def visit_default(self, node: Any) -> None:
            self.visits.append(("default", node))

        @on_visit(B)
        def visit_b(self, node: B) -> None:
            self.visits.append(("vb", node))

        @on_visit(C)
        def visit_c(self, node: C) -> None:
            self.visits.append(("vc", node))

    # extend visitor through inheritance
    class Visitor(VisitorBase):
        @on_visit(A)
        def visit_a(self, node: A) -> None:
            self.visits.append(("va", node))
            for elem in node.elems:
                self.visit(elem)

    tree = ex1()

    vb = VisitorBase()
    vb.visit(tree)
    assert vb.visits == [("default", tree)], "no A handler, should use default"

    vb.visits = []
    vb.visit(B("b1"))
    assert vb.visits == [("vb", B("b1"))], "has a B handler, should use"

    v = Visitor()

    @dataclass
    class D:
        label: str

    tree.elems.append(D("d1"))
    v.visit(tree)
    expected_visits = []

    def visit_elem(e):
        if isinstance(e, A):
            yield "va", e
            for elem in e.elems:
                yield from visit_elem(elem)
        elif isinstance(e, B):
            yield "vb", e
        elif isinstance(e, C):
            yield "vc", e
        else:
            yield "default", e

    for entry in visit_elem(tree):
        expected_visits.append(entry)

    assert v.visits == expected_visits


def test_visit_adv_inheritance_override():
    """
    Test that visitor can override a handler from the base visitor
    and that the base visitor remains unaffected.
    """

    class VisitorBase(NodeVisitor):
        def __init__(self):
            self.visits = []

        def visit_default(self, node: Any) -> None:
            self.visits.append(("default", node))

        @on_visit(A)
        def visit_a(self, node: A) -> None:
            self.visits.append(("va", node))
            for elem in node.elems:
                self.visit(elem)

        @on_visit(B)
        def visit_b(self, node: B) -> None:
            self.visits.append(("vb", node))

        @on_visit(C)
        def visit_c(self, node: C) -> None:
            self.visits.append(("vc", node))

    # extend visitor through inheritance
    class Visitor(VisitorBase):
        @on_visit(C)
        def visit_c(self, node: C) -> None:
            self.visits.append(("vc'", node))

    tree = ex1()

    vb = VisitorBase()
    vb.visits = []
    vb.visit(C("c1"))
    assert vb.visits == [("vc", C("c1"))], "should use handler of base class"

    v = Visitor()

    @dataclass
    class D:
        label: str

    tree.elems.append(D("d1"))
    v.visit(tree)
    expected_visits = []

    def visit_elem(e):
        if isinstance(e, A):
            yield "va", e
            for elem in e.elems:
                yield from visit_elem(elem)
        elif isinstance(e, B):
            yield "vb", e
        elif isinstance(e, C):
            yield "vc'", e
        else:
            yield "default", e

    for entry in visit_elem(tree):
        expected_visits.append(entry)

    assert v.visits == expected_visits


def test_visit_handle_multi_1():
    """test ability to use same handler for multiple node types"""

    class Visitor(NodeVisitor):
        def __init__(self):
            self.visits = []

        def visit_default(self, node: Any) -> None:
            self.visits.append(("default", node))

        @on_visit(A)
        def visit_a(self, node: A) -> None:
            self.visits.append(("va", node))
            for elem in node.elems:
                self.visit(elem)

        @on_visit(B, C)
        def visit_b(self, node: B) -> None:
            self.visits.append(("vbc", node))

    v = Visitor()
    tree = ex1()

    @dataclass
    class D:
        label: str

    tree.elems.append(D("d1"))
    v.visit(tree)
    expected_visits = []

    def visit_elem(e):
        if isinstance(e, A):
            yield "va", e
            for elem in e.elems:
                yield from visit_elem(elem)
        elif isinstance(e, (B, C)):
            yield "vbc", e
        else:
            yield "default", e

    for entry in visit_elem(tree):
        expected_visits.append(entry)

    assert v.visits == expected_visits


def test_visit_handle_multi_2():
    """test ability to use same handler for multiple node types"""

    class Visitor(NodeVisitor):
        def __init__(self):
            self.visits = []

        def visit_default(self, node: Any) -> None:
            self.visits.append(("default", node))

        @on_visit(A)
        def visit_a(self, node: A) -> None:
            self.visits.append(("va", node))
            for elem in node.elems:
                self.visit(elem)

        @on_visit(C)
        @on_visit(B)
        def visit_b(self, node: B) -> None:
            self.visits.append(("vbc", node))

    v = Visitor()
    tree = ex1()

    @dataclass
    class D:
        label: str

    tree.elems.append(D("d1"))
    v.visit(tree)
    expected_visits = []

    def visit_elem(e):
        if isinstance(e, A):
            yield "va", e
            for elem in e.elems:
                yield from visit_elem(elem)
        elif isinstance(e, (B, C)):
            yield "vbc", e
        else:
            yield "default", e

    for entry in visit_elem(tree):
        expected_visits.append(entry)

    assert v.visits == expected_visits


def test_visit_method_override():
    """
    Visitor handlers must be given unique method names. Otherwise, if multiple
    methods are defined using the same name, only the last method defined is
    retained.
    """

    class Visitor(NodeVisitor):
        def __init__(self):
            self.visits = []

        def visit_default(self, node: Any) -> None:
            self.visits.append(("default", node))

        @on_visit(B)
        def visit_b(self, node):
            self.visits.append(("b", node))

        @on_visit(C)
        def visit_b(self, node):
            return self.visits.append(("c", node))

    v = Visitor()
    v.visit(B("b1"))
    # defining `visit_b` again (but actually handling nodes of type C)
    # clobbers the first definition.
    assert v.visits == [("default", B("b1"))]


def test_handler_must_match_exact_type():
    """
    Test that handlers only match on *exact* types.
    """

    class Visitor(NodeVisitor):
        def __init__(self):
            self.visits = []

        def visit_default(self, node: Any) -> None:
            self.visits.append(("default", node))

        @on_visit(B)
        def visit_b(self, node):
            self.visits.append(("b", node))

    class B2(B):
        ...

    b2 = B2("b2_1")
    v = Visitor()
    v.visit(b2)
    assert v.visits == [("default", b2)]


def test_handler_cannot_be_wrapped():
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

    class Visitor(NodeVisitor):
        def __init__(self):
            self.visits = []

        def visit_default(self, node: Any) -> None:
            self.visits.append(("default", node))

        @some_decorator
        @on_visit(B)
        def visit_b(self, node):
            self.visits.append(("b", node))

    v = Visitor()
    v.visit(B("b1"))
    # decorator obscures the fact that `visit_b` was defined as a handler
    assert v.visits == [("default", B("b1"))]

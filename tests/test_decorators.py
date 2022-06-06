import pytest
from gcgen.decorators import snippet, has_snippet, is_snippet, is_generator, generator


def test_has_snippet_on_snippetfn():
    @snippet("one")
    @snippet("two")
    def foo():
        pass

    assert has_snippet(foo, "one")
    assert has_snippet(foo, "two")
    assert not has_snippet(foo, "else")


def test_has_snippet_on_fn():
    def foo():
        pass

    assert not has_snippet(foo, "one")
    assert not has_snippet(foo, "bar")


def test_is_snippetfn():
    @snippet("one")
    def foo():
        pass

    def bar():
        pass

    assert is_snippet(foo)
    assert not is_snippet(bar)


def test_is_generator():
    @generator
    def foo():
        pass

    def bar():
        pass

    assert is_generator(foo)
    assert not is_generator(bar)

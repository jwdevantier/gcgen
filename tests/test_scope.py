import pytest
from gcgen.scope import Scope


def test_scope_1layer_empty():
    s = Scope()

    assert "one" not in s, "'one' should not be in scope"
    assert s.get("one", "NO-VAL") == "NO-VAL"

    with pytest.raises(KeyError):
        s["one"]

    del s["one"]


def test_scope_1layer_get_set_del():
    s = Scope()
    assert "one" not in s
    s["one"] = None
    assert "one" in s
    assert s["one"] is None
    s["one"] = 1
    assert s["one"] is 1
    del s["one"]
    assert "one" not in s


def test_scope_2layer():
    s1 = Scope()
    s2 = s1.derive()
    assert "one" not in s2
    s1["one"] = 1
    assert "one" in s2
    assert s2["one"] is 1
    s2["one"] = 11
    assert s2["one"] == 11
    del s2["one"]
    assert "one" not in s2
    assert "one" in s1

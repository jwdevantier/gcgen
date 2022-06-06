from typing import Set


def has_snippet(f, name: str) -> bool:
    """true iff `f` has snippet"""
    snippets = getattr(f, "_gcgen", {}).get("snippets", set())
    return name in snippets


def is_snippet(f) -> bool:
    """true iff. function is decorated as one or more snippets"""
    return callable(f) and len(getattr(f, "_gcgen", {}).get("snippets", set())) != 0


def snippet_names(f) -> Set[str]:
    if not callable(f):
        return set()
    return getattr(f, "_gcgen", {}).get("snippets", set())


def snippet(name: str):
    """Mark decorated callable as a snippet.

    This decorator does nothing except install some attributes on the
    callable, identifying it as a snippet.

    Args:
        name: the name to identify the snippet by.
            (Note) can decorate multiple times to provide aliases

    Returns:
        A decorator function.
    """

    def decorator(f):
        cg_attr = f._gcgen = getattr(f, "_gcgen", {})
        snippets = cg_attr["snippets"] = cg_attr.get("snippets", set())
        snippets.add(name)

        return f

    return decorator


def is_generator(f) -> bool:
    return callable(f) and getattr(f, "_gcgen", {}).get("generator", False)


def generator(f):
    """Mark decorated callable as a generator.

    This decorator does nothing except install an attribute on the callable,
    identifying it as a generator.
    """
    cg_attr = f._gcgen = getattr(f, "_gcgen", {})
    cg_attr["generator"] = True

    return f

from gcgen.scope import Scope
from gcgen.emitter import Emitter
from gcgen.api.types import Json
from typing import Callable


SnippetFn = Callable[[Emitter, Scope, Json], None]


unset = object()


def get_snippet(scope: Scope, snippet: str, default=unset) -> SnippetFn:
    """dynamically resolve definition of snippet `snippet`.

    NOTE: snippets resolving other snippets using this function allow
    configuration files in subdirectories to override those snippets
    in their local context.
    This can provide local contexts the freedom to reuse a global/
    common snippet, while overriding specific parts refactored
    out as other snippets which are resolved dynamically.
    """
    if "$snippets" not in scope:
        raise RuntimeError("scope does not have a $snippets key!")
    snippet = scope["$snippets"].get(snippet, default=default)
    if snippet is unset:
        raise KeyError(snippet)
    return snippet

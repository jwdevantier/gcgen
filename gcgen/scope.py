from functools import reduce

_TOMBSTONE = object()


class Scope:
    """
    A scope is a form of layered dictionary, where derived/child scopes
    indirectly inherit all entries visible from the parent scope, with the
    ability to add new entries, override entries and delete entries, all
    without changing any of the parent scopes.
    """

    def __init__(self):
        self._dict = {}
        self._outer = None

    def derive(self) -> "Scope":
        """Create a child scope with this scope as its parent.

        Returns:
            The newly created child scope.
        """
        s = Scope()
        s._outer = self
        return s

    def copy(self) -> "Scope":
        """Create a shallow copy of scope.

        Returns:
            A shallow copy of this scope.
        """
        s = Scope()
        s._dict = {**self._dict}
        s._outer = self._outer
        return s

    def __setitem__(self, key, item):
        self._dict[key] = item

    def __getitem__(self, key):
        """Get scope entry identified by `key`.

        Implements support for the subscript notation (scope["key"]).

        Args:
            key: key to look for

        Raises:
            KeyError: if no entry could be found.

        Returns:
            Corresponding value if found, KeyError if not.
        """
        s = self
        while s is not None:
            if key not in s._dict:
                s = s._outer
                continue
            val = s._dict.get(key)
            if val == _TOMBSTONE:
                break
            return val
        raise KeyError(str(key))

    def get(self, key, default=None):
        """Get entry in scope identified by `key`.

        Args:
            key: key identifying to value to get
            default: the value to return if the entry is not found

        Returns:
            The value associated `key` or the given `default` value.
        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __delitem__(self, key):
        """Delete entry identified by `key`.

        Note: unlike a regular dictionary, we do not raise a KeyError if the
        entry is found in this scope. Definitively determining whether an
        entry is defined would require a full lookup in the scope and up all
        parent scopes until finding an entry or giving up.
        Always installing a TOMBSTONE entry directly into the scope is cheaper.

        Args:
            key: key identifying the entry to delete

        Returns:
            None
        """
        self._dict[key] = _TOMBSTONE

    def __contains__(self, key) -> bool:
        """True if key is defined in scope, false otherwise."""
        s = self
        while s:
            if key not in s._dict:
                s = s._outer
                continue
            val = s._dict[key]
            return val != _TOMBSTONE
        return False

    def update(self, other: dict):
        """Update scope with all entries from `other`."""
        self._dict.update(other)

    def to_dict(self) -> dict:
        """flatten scopes out to a dict."""
        dicts = []
        s = self
        while s:
            dicts.append(s._dict)
            s = s._outer
        dicts.reverse()

        return {k: v for d in dicts for k, v in d.items() if v != _TOMBSTONE}


__all__ = ["Scope"]

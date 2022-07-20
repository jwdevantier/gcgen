"""
Utilities for traversing and manipulating trees.

It can be helpful to operate on an input model as if it were akin to an
abstract syntax tree (AST), arranging the transformation from raw input to one
(or more) output forms as a series of transformations.
This is how multi-pass compilers work, where the overall transformation is
laid out as a series of discrete steps, each of which becomes easier to
debug and maintain.

Similarly, this approach can be helpful in massaging an input model into one
or more output models which ease code-generation.

Steps such as data validation and emitting the final code is best done using
classes deriving from the `NodeVisitor` class, while transformations, defined
as the transition from one kind of node to another, is best implemented by
deriving from the `NodeTransformer` class.

See tests for examples of use.
"""
import functools
from typing import Any, Union, List


TreeOp = Union["NodeVisitor", "NodeTransformer"]


class OnDispatch:
    def __init__(self, node_type, method):
        self.node_types = [node_type]
        self.__method = method

    @property
    def method(self):
        return self.__method

    def __call__(self, *args, **kwargs):
        return self.__method(*args, **kwargs)


class OnVisit(OnDispatch):
    ...


class OnTransform(OnDispatch):
    ...


def on_visit(node_type, *node_types):
    """Mark method as handler for visits of nodes of type `node_type` or in `node_types`.

    Use this decorator on methods in a `NodeVisitor` class to mark methods as
    handlers for calls to `visit` when providing `node_type` or any of the types
    in `node_types`.

    Args:
        node_type: node_type for which this handler should be used
        *node_types: (optional) additional node_types for which to use this handler

    Returns:
        A decorated handler object.
    """

    def decorator(f):
        if isinstance(f, OnVisit):
            wrapper = f
            wrapper.node_types.append(node_type)
        else:
            wrapper = OnVisit(node_type, f)
            functools.update_wrapper(wrapper, f)

        for nt in node_types:
            wrapper.node_types.append(nt)
        return wrapper

    return decorator


def on_transform(node_type, *node_types):
    """Mark method as handler for transformations of nodes of type `node_type` or in `node_types`.

    Use this decorator on methods in a `NodeTransformer` class to mark methods as
    handlers for calls to `transform` when providing `node_type` or any of the types
    in `node_types`.

    Args:
        node_type: node_type for which this handler should be used
        *node_types: (optional) additional node_types for which to use this handler

    Returns:
        A decorated handler object.
    """

    def decorator(f):
        if isinstance(f, OnTransform):
            wrapper = f
            wrapper.node_types.append(node_type)
        else:
            wrapper = OnTransform(node_type, f)
            functools.update_wrapper(wrapper, f)

        for nt in node_types:
            wrapper.node_types.append(nt)

        return wrapper

    return decorator


class NodeVisitorMeta(type):
    def __new__(cls, name, bases, dct):
        typ = super().__new__(cls, name, bases, dct)

        base_handlers = (getattr(b, "__visitors", {}) for b in bases)
        visitors = {}

        for bh in base_handlers:
            visitors.update(bh)

        for val in dct.values():
            if not isinstance(val, OnVisit):
                continue
            for node_type in val.node_types:
                visitors[node_type] = val

        setattr(typ, "__visitors", visitors)

        return typ

    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)

        # bind handler methods on object, this allows calling e.g. `obj.visit_a(node)`
        # as opposed to `obj.visit_a(obj, node)`.
        for ident, val in {ident: getattr(obj, ident) for ident in dir(obj)}.items():
            if isinstance(val, OnVisit):
                setattr(obj, ident, val.method.__get__(obj))

        return obj


class NodeVisitor(metaclass=NodeVisitorMeta):
    """Base class with which to implement a visitor.

    Implement a visitor, a type of class capable of traversing a tree by
    using a series of visit operations, one per type of node, to traverse the tree.
    Visitors are especially useful for implementing validation of nodes in the
    tree and for traversing trees as part of the code-generation step.

    To start traversal, pass the tree to the `visit` method.
    Traversal works by defining a `visit` method on the visitor for each
    type of node, which in turn calls `visit` on each of its child nodes
    to continue traversing down the tree.
    This approach is named visitor after the GoF "Visitor" pattern.

    Note:
        For every node for which there is no specific handler, `visit_default`
        is called. The default behavior of `visit_default` is to raise a
        `NotImplementedError`.
        To install a visit handler, write a method taking 1 argument, `node`,
        and decorate it using the `on_visit()` decorator, passing the decorator
        one or more `Type` objects (~classes), marking the types of nodes to
        handle using the method.

    Note:
        * inheritance works (unlike functools.singledispatchmethod)
            * handlers are inherited, and can be overridden
        * method names of handlers MUST remain unique. If defining several
          handlers using the same method name, only the last handler is retained.
        * handlers must be decorated with `on_visit` as the _last_ decorator,
          wrapping handlers in other decorators breaks the ability to identify
          a method as a handler.
        * a single handler can handle multiple types of nodes, either by:
            * decorating the handler multiple times using `@on_visit(...)`
            * passing multiple arguments to `@on_visit(...)`
    """

    def visit_default(self, node: Any) -> None:
        """Default visit function for nodes of types for which there is no specific visit function.

        This method defines the default action when calling `visit` on a node for
        which handler has been defined for the node's exact type.
        The default behavior is to raise an error, but this method may be overridden
        by a deriving class to e.g. trigger a NOOP.

        Args:
            node: the node to visit. This node is of a type for which the visitor
                  has no existing `visit` function.

        Returns:
            None
        """
        raise NotImplementedError(f"visit {type(node).__name__} not implemented.")

    def visit(self, node: Any) -> None:
        """Visit node `node`.

        Visit node. If a specific handler is registered for the node's exact type,
        use it. Otherwise, call `visit_default`.

        Args:
            node: the node to visit

        Returns:
            None
        """
        m = getattr(self, "__visitors").get(type(node))
        if m is None:
            self.visit_default(node)
            return
        # pass `self` explicitly as 'methods' are not bound
        m(self, node)


class NodeTransformerMeta(type):
    """Base class with which to implement a transformer.

    Implement a transformer, a type of class capable of traversing a tree and
    to replace some/all of the traversed nodes as it does so.
    Transformers are especially useful for implementing rewrite operations where
    specific nodes are replaced/modified to make subsequent parsing and eventually
    code generation easier.

    To start traversal, pass the tree to the `transform` method.
    Traversal works by defining a `transform` method on the transformer for each
    type of node, which in turn calls `transform` on each of its child nodes
    to continue traversing down the tree. The return value of each transform
    handler should be the transformed sub-tree.
    In this way, parts or all of the tree may be transformed as part of the
    operation.

    Note:
        For every node for which there is no specific handler, `visit_default`
        is called. The default behavior of `visit_default` is to raise a
        `NotImplementedError`.
        To install a visit handler, write a method taking 1 argument, `node`,
        and decorate it using the `on_visit()` decorator, passing the decorator
        one or more `Type` objects (~classes), marking the types of nodes to
        handle using the method.

    Note:
        * inheritance works (unlike functools.singledispatchmethod)
            * handlers are inherited, and can be overridden
        * method names of handlers MUST remain unique. If defining several
          handlers using the same method name, only the last handler is retained.
        * handlers must be decorated with `on_visit` as the _last_ decorator,
          wrapping handlers in other decorators breaks the ability to identify
          a method as a handler.
        * a single handler can handle multiple types of nodes, either by:
            * decorating the handler multiple times using `@on_visit(...)`
            * passing multiple arguments to `@on_visit(...)`
    """

    def __new__(cls, name, bases, dct):
        typ = super().__new__(cls, name, bases, dct)

        base_handlers = (getattr(b, "__transformers", {}) for b in bases)
        transformers = {}

        for bh in base_handlers:
            transformers.update(bh)

        for val in dct.values():
            if not isinstance(val, OnTransform):
                continue
            for node_type in val.node_types:
                transformers[node_type] = val

        setattr(typ, "__transformers", transformers)

        return typ

    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)

        # bind handler methods on object, this allows calling e.g. `obj.visit_a(node)`
        # as opposed to `obj.visit_a(obj, node)`.
        for ident, val in {ident: getattr(obj, ident) for ident in dir(obj)}.items():
            if isinstance(val, OnTransform):
                setattr(obj, ident, val.method.__get__(obj))

        return obj


class NodeTransformer(metaclass=NodeTransformerMeta):
    def transform_default(self, node: Any) -> Any:
        """Default transform function for nodes of types for which there is no specific transform function.

        This method defines the default action when calling `transform` on a node for
        which handler has been defined for the node's exact type.
        The default behavior is to raise an error, but this method may be overridden
        by a deriving class to e.g. return back the same object.

        Args:
            node: the node to transform. This node is of a type for which the transformer
                  has no existing `transform` function.

        Returns:
            Raises the `NotImplementedError`
        """
        raise NotImplementedError(f"transform {type(node).__name__} not implemented.")

    def transform(self, node: Any) -> Any:
        """Transform node `node`.

        Transform node. If a specific handler is registered for the node's exact type,
        use it. Otherwise, call `transform_default`.

        Args:
            node: the node to transform

        Returns:
            The result of calling the transform handler, may be a new, transformed
            node, may be the same node.
        """
        m = getattr(self, "__transformers").get(type(node))
        if m is None:
            return self.transform_default(node)
        # pass `self` explicitly as 'methods' are not bound
        return m(self, node)


def parse_tree(pipeline: List[TreeOp], tree: Any) -> Any:
    """Parse tree by applying a series of visitors and transformers.

    Args:
        pipeline: A series of operations to perform on the tree, each of which
                  is a visitor or transformer.
        tree: The input tree/model.

    Returns:
        The resulting tree/model from applying each operation in order.
    """
    for step in pipeline:
        if isinstance(step, NodeTransformer):
            tree = step.transform(tree)
        elif isinstance(step, NodeVisitor):
            step.visit(tree)
        else:
            raise RuntimeError(f"{type(step)!r}, expected NodeTransformer|NodeVisitor")
    return tree


__all__ = [
    "TreeOp",
    "on_visit",
    "on_transform",
    "NodeVisitor",
    "NodeTransformer",
    "parse_tree",
]

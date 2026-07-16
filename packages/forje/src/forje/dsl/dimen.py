from forje.dsl import Module

__all__ = ["module"]

module = Module(name="dimen", priority=-1000).export_starlark(
    package=__name__,
    resource_name="dimen.star",
)

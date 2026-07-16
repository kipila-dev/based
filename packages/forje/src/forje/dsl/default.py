from forje.dsl import Module

__all__ = ["module"]

module = Module(name=None, priority=-998).export_starlark(
    package=__name__,
    resource_name="default.star",
)

from forje.dsl import Module

__all__ = ["module"]

module = Module(name="tailwind").export_starlark(
    package=__name__,
    resource_name="tailwind.star",
)

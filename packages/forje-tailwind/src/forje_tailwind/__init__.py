from forje.dsl import Module

__version__ = "1.0.0"
__all__ = ["module"]

module = Module(name="tailwind").export_starlark(
    package=__name__,
    resource_name="tailwind.star",
)

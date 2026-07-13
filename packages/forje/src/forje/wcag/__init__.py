from forje.dsl import Module

from .wcag import WCAGValidation

__all__ = ["WCAGValidation", "module"]

module = Module(name="wcag").export_starlark(
    package=__name__,
    resource_name="wcag.star",
)

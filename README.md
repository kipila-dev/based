# Forje

**A build system for your design system.**

Define your design tokens once, compile to native artifacts automatically. Build
scripts are written in [Starlark](https://bazel.build/rules/language), the same
language used by Bazel and Buck2.

```starlark
primary = Token("primary", Color("#38BDF8"))
surface = Token("surface", dark=Color("#0F172A"), light=Color("#FFFFFF"))

target(
    id="acme",
    tokens=[primary, surface],
    artifacts=[
        Artifact("android", "dist/acme/android"),
        Artifact("apple", "dist/acme/apple"),
        Artifact("css", "dist/acme/css"),
    ],
)
```

## Installation

```sh
pip install forje
```

Requires Python 3.12+.

## Usage

Create a `build.forje` in your project root and run:

```sh
forje build
```

## WCAG Contrast Validation

Forje supports accessibility testing by letting you declare contrast
requirements directly on your tokens using the `wcag` API.

```starlark
load("wcag", "wcag")

surface = Token("surface", Color("#FFFFFF"))
primary = Token("primary", Color("#0284C7"))
text = Token(
    "text",
    Color("#1E293B"),
    context=wcag.against(surface, role=wcag.Role.Text, level=wcag.Level.AA)
)

target(
    id="acme",
    tokens=[surface, primary, text],
    artifacts=[Artifact("android", "acme/res")],
)
```

If `text` fails to meet the AA contrast ratio against `surface` during the
compile step, Forje will raise a validation error.

## Extending Forje

Plugins expose new DSL functions, compiler passes and backends via Python entry
points. For a reference plugin implementation, see the built-in `forje.wcag`
module.

```toml
# DSL extension
[project.entry-points."forje.dsl"]
myplugin = "myplugin.dsl:myplugin_module"

# Compiler pass
[project.entry-points."forje.pass"]
myplugin = "myplugin.passes:MyValidation"

# Platform backend
[project.entry-points."forje.backend"]
myplatform = "myplugin.backend:MyPlatformBackend"
```

The following plugins are maintained alongside Forje and can be installed
directly:

- [`forje-tailwind`](https://github.com/kipila-dev/forje/tree/main/packages/forje-tailwind):
  Tailwind CSS color palette

## License

MIT

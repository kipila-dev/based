# Forje

**A compiler pipeline for design systems.**

Design tokens are source code. Forje treats your design system as a compilable
program instead of a collection of transformation scripts. It parses build
definitions into an intermediate representation, executes validation and
transformation passes, and emits platform-specific artifacts. Build definitions
are written in [Starlark](https://bazel.build/rules/language), the same language
used by Bazel and Buck2.

Colors are stored in a device-independent representation and converted to each
target color space during compilation. Wide-gamut colors are preserved for
targets that support them and clipped when converted to narrower gamuts such as
sRGB.

```starlark
primary = Token("primary", color.oklch(0.78, 0.30, 225))
surface = Token("surface", dark=Color("#0F172A"), light=Color("#FFFFFF"))

target(
    id="acme",
    tokens=[primary, surface],
    artifacts=[
        Artifact("android", "dist/acme/android"),
        Artifact("apple", "dist/acme/apple"),
        Artifact(
            "compose",
            "dist/acme/compose",
            package="com.acme.android.design"
        ),
        Artifact("css", "dist/acme/css"),
    ],
)
```

## Installation

```bash
pip install forje
```

Requires Python 3.12+.

## Usage

Create a `build.forje` in your project root and run:

```bash
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

Plugin interface is exposed via Python entry points. For a reference plugin
implementation, see the built-in `forje.wcag` module.

```toml
# DSL extension
[project.entry-points."forje.dsl"]
myplugin = "myplugin.dsl:myplugin_module"

# Context adapter
[project.entry-points."forje.context_adapter"]
mynode = "myplugin.models:mynode_adapter"

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

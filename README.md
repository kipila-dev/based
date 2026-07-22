# Forje

**A compiler pipeline for design systems.**

Design tokens are source code. Forje treats your design system as a compilable
program instead of a collection of transformation scripts. It parses build
definitions into an intermediate representation, executes validation and
transformation passes, and emits platform-specific artifacts. Build definitions
are written in [Starlark](https://bazel.build/rules/language), the same language
used by Bazel and Buck2.

Values are stored in typed, device-independent representations and converted
into target-specific forms during compilation. Colors preserve their source
color space, with wide-gamut values retained for targets that support them and
clipped when converted to narrower gamuts such as sRGB.

Dimensions are typed by semantic kinds (`spacing`, `size`, `font`). This allows
backends to choose appropriate units during generation while keeping the source
definition independent of implementation details.

```starlark
colors = [
    Token(
        "primary",
        light=color.Oklch(0.5, 0.134, 242.749),
        dark=color.Oklch(0.828, 0.111, 230.318),
    ),
    Token(
        "surface",
        light=color.Oklch(0.97, 0, 0),
        dark=color.Oklch(0.205, 0, 0),
    ),
]

space = [
    Token("space.s", dimen.Spacing(0.5)),
    Token("space.m", dimen.Spacing(1)),
    Token("space.l", dimen.Spacing(2)),
    Token("space.xl", dimen.Spacing(4)),
]

target(
    id="acme",
    tokens=colors + space,
    artifacts=[
        Artifact("android", "dist/acme/android"),
        Artifact("apple", "dist/acme/apple"),
        Artifact("compose", "dist/acme/compose", package="com.acme.android.design"),
        Artifact("css", "dist/acme/css"),
    ],
)
```

Forje emits platform-native representations from the source code:

```css
:root {
  --dimen-space-s: 0.5rem;
  --dimen-space-m: 1rem;
  --dimen-space-l: 2rem;
  --dimen-space-xl: 4rem;
}

:root {
  --color-primary: rgb(0 105 168);
  --color-surface: rgb(245 245 245);
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-primary: rgb(116 212 255);
    --color-surface: rgb(23 23 23);
  }
}

:root[data-theme="light"] {
  --color-primary: rgb(0 105 168);
  --color-surface: rgb(245 245 245);
}

:root[data-theme="dark"] {
  --color-primary: rgb(116 212 255);
  --color-surface: rgb(23 23 23);
}

@supports (color: oklch(0% 0 0)) {
  :root {
    --color-primary: oklch(0.5 0.134 242.749);
    --color-surface: oklch(0.97 0 none);
  }

  @media (prefers-color-scheme: dark) {
    :root {
      --color-primary: oklch(0.828 0.111 230.318);
      --color-surface: oklch(0.205 0 none);
    }
  }

  :root[data-theme="light"] {
    --color-primary: oklch(0.5 0.134 242.749);
    --color-surface: oklch(0.97 0 none);
  }

  :root[data-theme="dark"] {
    --color-primary: oklch(0.828 0.111 230.318);
    --color-surface: oklch(0.205 0 none);
  }
}
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
    annotations=wcag.against(surface, role=wcag.Role.Text, level=wcag.Level.AA)
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

# Annotations adapter
[project.entry-points."forje.annotations_adapter"]
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

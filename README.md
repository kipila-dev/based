# based.

`based` is a Build System for Design.

Build scripts are written in Starlark:

```starlark
palette = struct(primary=color.Oklch(0.5, 0.134, 242.749))
tokens = [Token("primary", light=palette.primary)]

target(
    id="acme",
    tokens=tokens,
    artifacts=[Artifact("css", "dist/acme/css")]
)
```

## Installation

```bash
pip install basedbuild
```

## Usage

Create a `build.based` in your project root and run:

```bash
based build
```

## WCAG Contrast Validation

`based` supports accessibility testing by letting you declare contrast
requirements using the `wcag` annotations.

```starlark
load("wcag", "wcag")

surface = Token("surface", Color("#FFFFFF"))
primary = Token("primary", Color("#0284C7"))
text = Token(
    "text",
    Color("#1E293B"),
    # Will raise a validation error if text fails to meet the AA contrast
    # ratio against surface.
    annotations=wcag.against(surface, role=wcag.Role.Text, level=wcag.Level.AA)
)

target(
    id="acme",
    tokens=[surface, primary, text],
    artifacts=[Artifact("android", "acme/res")],
)
```

## Extending `based`

Plugin interface is exposed via Python entry points. For a reference plugin
implementation, see the built-in `wcag` module.

```toml
# DSL extension
[project.entry-points."based.dsl"]
myplugin = "myplugin.dsl:myplugin_module"

# Type adapter
[project.entry-points."based.adapter"]
mynode = "myplugin.models:mynode_adapter"

# Compiler pass
[project.entry-points."based.pass"]
myplugin = "myplugin.passes:MyValidation"

# Platform backend
[project.entry-points."based.backend"]
myplatform = "myplugin.backend:MyPlatformBackend"
```

The following plugins are maintained alongside `based` and can be installed
directly:

- [`basedbuild-tailwind`](https://github.com/kipila-dev/based/tree/main/packages/based-tailwind):
  Tailwind CSS v4 color palette

## Advanced Example

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

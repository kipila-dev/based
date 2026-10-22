# based-tailwind

Tailwind CSS v4 color palette plugin for `based`.

## Installation

```bash
pip install basedbuild-tailwind
```

## Usage

Load the plugin and reference colors via `tailwind.color.<name>.<shade>`:

```starlark
load("tailwind", "tailwind")

primary = Token("primary", tailwind.color.blue.c500)

target(
    id="acme",
    tokens=[primary],
    artifacts=[Artifact("css", "dist/assets")],
)
```

For the full list of available colors, see the
[Tailwind CSS documentation](https://tailwindcss.com/docs/colors).

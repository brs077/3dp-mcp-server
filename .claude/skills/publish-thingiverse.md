# publish-thingiverse

Publish a model to Thingiverse.

## When to use

Use when the user wants to upload and share their model on Thingiverse.

## Instructions

1. Call `publish_thingiverse` with the model name and listing details
2. Requires `THINGIVERSE_TOKEN` environment variable (OAuth access token)
3. Publishes as work-in-progress by default for safety

## Parameters

- `name` (required): Model name (must exist in session)
- `title` (required): Thing title on Thingiverse
- `description` (default: `""`): Thing description (supports markdown)
- `tags` (default: `'["3dprinting"]'`): JSON list of tags
- `category` (default: `"3D Printing"`): Thingiverse category name
- `is_wip` (default: `True`): Publish as work-in-progress draft

## Example

```
publish_thingiverse(
  name="bracket",
  title="Universal Mounting Bracket",
  description="Parametric mounting bracket for 2020 extrusion",
  tags='["bracket", "2020", "mounting"]',
  is_wip=True
)
```

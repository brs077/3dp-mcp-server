# publish-cults3d

Publish a model to Cults3D via their GraphQL API.

## When to use

Use when the user wants to create a listing on Cults3D for their model.

## Instructions

1. Call `publish_cults3d` with the model name and listing details
2. Requires `CULTS3D_API_KEY` environment variable
3. Creates a draft listing — file upload must be done manually via the web interface

## Parameters

- `name` (required): Model name (must exist in session)
- `title` (required): Creation title on Cults3D
- `description` (default: `""`): Creation description (HTML allowed)
- `tags` (default: `'["3dprinting"]'`): JSON list of tags
- `license` (default: `"creative_commons_attribution"`): License type
- `free` (default: `True`): Publish as free model
- `price_cents` (default: `0`): Price in cents (only used if `free=False`)

## Example

```
publish_cults3d(
  name="bracket",
  title="Universal Mounting Bracket",
  description="<p>Parametric bracket for 2020 extrusion</p>",
  tags='["bracket", "mounting"]',
  free=True
)
```

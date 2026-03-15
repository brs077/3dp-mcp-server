# publish-myminifactory

Publish a model to MyMiniFactory.

## When to use

Use when the user wants to upload and share their model on MyMiniFactory.

## Instructions

1. Call `publish_myminifactory` with the model name and listing details
2. Requires `MYMINIFACTORY_TOKEN` environment variable
3. Publishes as draft

## Parameters

- `name` (required): Model name (must exist in session)
- `title` (required): Object title on MyMiniFactory
- `description` (default: `""`): Object description
- `tags` (default: `'["3dprinting"]'`): JSON list of tags
- `category_id` (default: `0`): MyMiniFactory category ID (0 = uncategorized)

## Example

```
publish_myminifactory(
  name="bracket",
  title="Universal Mounting Bracket",
  description="Parametric bracket for 2020 extrusion",
  tags='["bracket", "mounting"]'
)
```

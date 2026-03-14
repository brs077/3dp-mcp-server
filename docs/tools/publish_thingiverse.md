# publish_thingiverse

Create a Thing on Thingiverse and upload the STL file.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | Yes | — | Model name (must exist in current session) |
| `title` | string | Yes | — | Thing title on Thingiverse |
| `description` | string | No | `""` | Thing description (supports markdown) |
| `tags` | string | No | `'["3dprinting"]'` | JSON list of tags |
| `category` | string | No | `"3D Printing"` | Thingiverse category name |
| `is_wip` | bool | No | `true` | Publish as work-in-progress (safe default) |

## Authentication

Requires `THINGIVERSE_TOKEN` environment variable — an OAuth access token.

1. Create an app at https://www.thingiverse.com/developers
2. Complete the OAuth flow to get an access token
3. Set: `export THINGIVERSE_TOKEN="your_token_here"`

## Example

```
publish_thingiverse(
    name="organizer",
    title="Desk Organizer with Pen Holder",
    description="A compact desk organizer with slots for pens and a phone stand.",
    tags='["organizer", "desk", "office"]',
    is_wip=true
)
```

## Response

```json
{
  "success": true,
  "thing_id": 12345678,
  "thing_url": "https://www.thingiverse.com/thing:12345678",
  "title": "Desk Organizer with Pen Holder",
  "file_uploaded": "organizer.stl",
  "is_wip": true,
  "note": "Published as WIP. Edit on Thingiverse to add images and finalize."
}
```

# publish_cults3d

Create a listing on Cults3D via their GraphQL API.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | Yes | — | Model name (must exist in current session) |
| `title` | string | Yes | — | Creation title on Cults3D |
| `description` | string | No | `""` | Creation description (HTML allowed) |
| `tags` | string | No | `'["3dprinting"]'` | JSON list of tags |
| `license` | string | No | `"creative_commons_attribution"` | License type |
| `free` | bool | No | `true` | Publish as free model |
| `price_cents` | int | No | `0` | Price in cents (only if `free=false`) |

## Authentication

Requires `CULTS3D_API_KEY` environment variable.

Get your API key from https://cults3d.com/en/pages/api

## Important Notes

Cults3D requires files to be hosted at a public URL — their API does not accept direct file uploads. This tool creates the listing as a draft. You must then upload the STL file manually through the Cults3D web interface.

## Example

```
publish_cults3d(
    name="bracket",
    title="Adjustable Wall Bracket",
    description="<p>A parametric wall bracket with M4 mounting holes.</p>",
    tags='["bracket", "wall mount", "functional"]',
    free=true
)
```

## Response

```json
{
  "success": true,
  "creation_id": "abc123",
  "creation_url": "https://cults3d.com/en/3d-model/...",
  "slug": "adjustable-wall-bracket",
  "title": "Adjustable Wall Bracket",
  "status": "draft",
  "stl_path": "/path/to/outputs/bracket.stl",
  "note": "Created as draft. Cults3D requires file upload through their web interface..."
}
```

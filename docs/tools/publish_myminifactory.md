# publish_myminifactory

Create an object on MyMiniFactory and upload the STL file.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | Yes | — | Model name (must exist in current session) |
| `title` | string | Yes | — | Object title on MyMiniFactory |
| `description` | string | No | `""` | Object description |
| `tags` | string | No | `'["3dprinting"]'` | JSON list of tags |
| `category_id` | int | No | `0` | MyMiniFactory category ID (0 = uncategorized) |

## Authentication

Requires `MYMINIFACTORY_TOKEN` environment variable — an OAuth access token.

Register at https://www.myminifactory.com/api-documentation for API access.

## Example

```
publish_myminifactory(
    name="gear_20t",
    title="20-Tooth Spur Gear Module 1",
    description="Involute spur gear, module 1, 20 teeth, 5mm thick.",
    tags='["gear", "mechanical", "spur"]'
)
```

## Response

```json
{
  "success": true,
  "object_id": 987654,
  "object_url": "https://www.myminifactory.com/object/3d-print-987654",
  "title": "20-Tooth Spur Gear Module 1",
  "file_uploaded": "gear_20t.stl",
  "status": "draft",
  "note": "Published as draft. Visit MyMiniFactory to add images, set category, and publish."
}
```

# publish_github_release

Upload model files to GitHub Releases as release assets.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `name` | string | Yes | — | Model name (must exist in current session) |
| `repo` | string | Yes | — | GitHub repo in `owner/repo` format |
| `tag` | string | Yes | — | Release tag (e.g. `v1.0.0`) |
| `description` | string | No | `""` | Release description/notes |
| `formats` | string | No | `'["stl", "step"]'` | JSON list of formats to upload |
| `draft` | bool | No | `false` | Create as draft release |

## Authentication

Uses one of two methods (checked in order):

1. **`gh` CLI** (preferred) — Install from https://cli.github.com and run `gh auth login`
2. **`GITHUB_TOKEN`** environment variable — Personal access token with `repo` scope

## Example

```
publish_github_release(
    name="bracket",
    repo="brs077/my-models",
    tag="bracket-v1.0",
    description="Wall-mount bracket, 3mm thick, M4 mounting holes"
)
```

## Response

```json
{
  "success": true,
  "method": "gh_cli",
  "release_url": "https://github.com/brs077/my-models/releases/tag/bracket-v1.0",
  "tag": "bracket-v1.0",
  "repo": "brs077/my-models",
  "files_uploaded": ["bracket.stl", "bracket.step"]
}
```

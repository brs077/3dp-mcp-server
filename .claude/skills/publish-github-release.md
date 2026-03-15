# publish-github-release

Publish a model to GitHub Releases.

## When to use

Use when the user wants to upload their 3D model files to a GitHub repository as a release.

## Instructions

1. Ensure the model exists and is exported
2. Call `publish_github_release` with repo and tag info
3. Requires `gh` CLI (preferred) or `GITHUB_TOKEN` env var

## Parameters

- `name` (required): Model name (must exist in session)
- `repo` (required): GitHub repo in `"owner/repo"` format
- `tag` (required): Release tag (e.g. `"v1.0.0"`)
- `description` (default: `""`): Release description/notes
- `formats` (default: `'["stl", "step"]'`): JSON list of formats to upload
- `draft` (default: `False`): Create as draft release

## Example

```
publish_github_release(
  name="bracket",
  repo="user/my-models",
  tag="v1.0.0",
  description="Initial release of mounting bracket",
  draft=False
)
```

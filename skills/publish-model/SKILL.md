---
name: publish-model
description: Publish or share a 3D model — upload to GitHub Releases, Thingiverse, MyMiniFactory, Cults3D, or search for existing models. Use when the user wants to share, publish, or find 3D models.
---

# Model Publishing & Discovery

Help the user publish their 3D models or discover existing models from the community.

## Workflow — Publishing

1. Call `list_models` to see available models
2. Confirm which model and platform the user wants to publish to
3. Call `export_model` to ensure both STL and STEP files are generated
4. Optionally call `export_drawing` to generate a technical drawing for the listing
5. Call the appropriate publish tool
6. Help the user write a good title, description, and tags

## Workflow — Discovery

1. Call `search_models` with the user's query to find existing models
2. Present results with titles, authors, download counts, and URLs
3. If the user wants to remix, suggest using `import_model` to bring it into the session

## Publishing Tools

| Tool | Platform | Auth Required |
|------|----------|---------------|
| `publish_github_release` | GitHub Releases | `gh` CLI or GITHUB_TOKEN |
| `publish_thingiverse` | Thingiverse | THINGIVERSE_TOKEN env var |
| `publish_myminifactory` | MyMiniFactory | MYMINIFACTORY_TOKEN env var |
| `publish_cults3d` | Cults3D | CULTS3D_API_KEY env var |

## Discovery Tools

| Tool | Purpose |
|------|---------|
| `search_models` | Search Thingiverse for existing models (requires THINGIVERSE_API_KEY) |

## Tips

- Always export both STL and STEP formats before publishing
- Suggest descriptive tags for discoverability (material, use case, printer type)
- Include dimensions and material recommendations in the description
- Add print settings (layer height, infill, supports) to help other users
- GitHub Releases is the easiest to set up — just needs `gh` CLI authenticated
- Generate a `section_view` or `export_drawing` to include as documentation images

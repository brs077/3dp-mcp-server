---
name: publish-model
description: Publish a 3D model to GitHub Releases, Thingiverse, MyMiniFactory, or Cults3D. Use when the user wants to share or publish their model.
---

# Model Publishing

Help the user publish their 3D model to a sharing platform.

## Workflow

1. Call `list_models` to see available models
2. Confirm which model and platform the user wants to publish to
3. Call `export_model` to ensure STL/STEP files are generated
4. Call the appropriate publish tool:
   - `publish_github_release` — requires `gh` CLI or GITHUB_TOKEN
   - `publish_thingiverse` — requires THINGIVERSE_TOKEN env var
   - `publish_myminifactory` — requires MYMINIFACTORY_TOKEN env var
   - `publish_cults3d` — requires CULTS3D_API_KEY env var
5. Help the user write a good title, description, and tags

## Tips

- Always export both STL and STEP formats before publishing
- Suggest descriptive tags for discoverability
- Include dimensions and material recommendations in the description

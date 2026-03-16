---
name: search-remix
description: Search for existing 3D models on Thingiverse for inspiration or remixing. Use when the user wants to find, browse, or get ideas from community models.
---

# Search & Remix

Help the user find existing 3D models for inspiration, reference, or remixing.

## Workflow

1. Call `search_models` with the user's query to find models on Thingiverse
2. Present results with titles, authors, download counts, and links
3. If the user wants to remix or build on an idea:
   - Help them design a new model inspired by the search results using `create_model`
   - Or import a downloaded file with `import_model` and modify it
4. Use `transform_model` or `combine_models` to adapt imported geometry
5. Run `analyze_printability` on the final result

## Tips

- Use specific search terms for better results (e.g., "M3 knurled thumb nut" not "nut")
- Requires `THINGIVERSE_API_KEY` environment variable — get one at https://www.thingiverse.com/developers
- Respect original model licenses when remixing — check the license on the Thingiverse page
- After remixing, use `publish-model` skill to share the result

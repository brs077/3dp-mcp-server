# search-models

Search for 3D models on Thingiverse.

## When to use

Use when the user wants to find existing 3D models for reference or inspiration.

## Instructions

1. Call `search_models` with the search query
2. Requires `THINGIVERSE_API_KEY` environment variable
3. Present results with title, author, URL, and like/download counts

## Parameters

- `query` (required): Search query string
- `source` (default: `"thingiverse"`): Search source (currently only Thingiverse)
- `max_results` (default: `10`): Maximum number of results to return

## Example

```
search_models(query="raspberry pi case", max_results=5)
```

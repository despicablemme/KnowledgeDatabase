---
name: media-search
description: Search and aggregate images or videos from multiple sources (Pexels + Pixabay) simultaneously. Use when user wants to find, search, or look up images, photos, pictures, videos, or footage. Searches both Pexels and Pixabay MCP servers via mcporter and returns combined results. Triggers on: "帮我找图", "搜索图片", "找一张照片", "搜视频", "帮我下载图片", "找张壁纸", etc.
---

# Media Search Skill

Search images/videos from **Pexels** and **Pixabay** simultaneously via mcporter, then aggregate and present results.

## Workflow

1. Parse the user's search query (extract keywords, orientation, size preferences)
2. Execute both searches in parallel via mcporter
3. Combine and deduplicate results
4. Present results with direct download URLs

## MCP Servers

This skill uses two pre-configured MCP servers via mcporter:

- **pexels** — `pexels-mcp-server`
- **pixabay** — `pixabay-mcp`

## Search Commands

### Search Photos

```bash
# Pexels
npx mcporter call pexels.searchPhotos query:"<keywords>" per_page:10 orientation:<landscape|portrait|square>

# Pixabay  
npx mcporter call pixabay.search_pixabay_images query:"<keywords>" per_page:10 orientation:<all|horizontal|vertical>
```

### Search Videos

```bash
# Pexels
npx mcporter call pexels.searchVideos query:"<keywords>" per_page:10

# Pixabay
npx mcporter call pixabay.search_pixabay_videos query:"<keywords>" per_page:10
```

## Result Aggregation

When combining results:
1. Merge both results into a single list
2. Sort by relevance/quality (prefer photos with more metadata)
3. Remove exact duplicates (same URL)
4. Present in format:

```
[Pexels] <photographer> - <description>
URL: <url>
尺寸: <width>x<height>

[Pixabay] <user> - <tags>
URL: <url>
```

## Output

Always include:
- Source (Pexels/Pixabay)
- Direct image/video URL
- Photographer/creator name
- Dimensions/size info
- Direct download link (append /download for Pexels)

## Notes

- Pexels API key configured: via acpx plugin
- Pixabay API key configured: via acpx plugin
- Both servers must be running through acpx runtime

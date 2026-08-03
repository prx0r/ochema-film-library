# Ochema Film Library

The pristine, machine-readable catalog of every film work in the Ochema corpus.
Everything lives here so we can curate, port to Skia, publish to YouTube, and
use the corpus as dev examples — without re-auditing the mess.

## Layout

```
library/
  index.json    — raw scan of every source location (scripts, packs, videos, sizes)
  works.json    — the canonical registry: 79 works, id/title/thesis/queue/rendered/skia/youtube status
works/          — (future) one dir per work: script + pack + stills + final mp4
analytics/      — YouTube analytics schema
scripts/        — scan.mjs (raw inventory), registry.mjs (works registry)
```

## The pipeline tiers

| Tier | What | Count | Where |
|------|------|-------|-------|
| PIL platinum films | hand-authored essay+render `.py` scripts | 79 | `/root/projects/clean/queue{1-4}/*_platinum.py` |
| PIL-rendered outputs | `output_<id>/` renders (final mp4s) | 21 of 79 | `/mnt/HC_Volume_106427611/goldrender/` |
| Featured on site | on R2 public + ochema-site | 16 platinum + 4 series shorts | `atlas-sources/videos/` (R2) |
| Skia (MOTHERFUCKER) | new renderer, PIL→Canvas2D spec exists | 0 ported yet | `/root/projects/clean/MOTHERFUCKER` + `gemma-skia-conversion.md` |
| Series pilot | what-the-heck-is films | 4 (1 long + 3 shorts) | `/root/projects/ochema/films/whattheheckisintelligence/` |

## Work status lifecycle

`pil → rendered → featured → skiaPorted → onSite → youtubeStatus`

- `pil`: script exists in a queue
- `rendered`: `goldrender/output_<id>/` exists
- `featured`: mp4 + thumb uploaded to `atlas-sources/videos|thumbnails` (public R2)
- `skiaPorted`: ported to MOTHERFUCKER scene pack
- `onSite`: shown on ochema-site
- `youtubeStatus`: unpublished / published / analytics attached

## Regenerate the catalog

```bash
node scripts/scan.mjs      # re-scan all source dirs -> library/index.json
node scripts/registry.mjs  # rebuild works registry -> library/works.json
```

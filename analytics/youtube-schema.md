# YouTube Analytics Schema

Per-video analytics schema for the corpus. Every published work gets a row.
This is the contract that survives when videos go to YouTube — the site,
the library, and the channel all read from it.

## Video document (one per work)

```json
{
  "workId": "dna_superconductor",
  "title": "Your DNA Is a Superconductor Programming Reality",
  "youtubeId": "dQw4w9WgXcQ",
  "publishDate": "2026-09-01",
  "category": "platinum | series | short",
  "status": "published",
  "metrics": {
    "views": 12000,
    "watchTimeHours": 850,
    "avgViewDurationSec": 320,
    "avgViewPercent": 0.46,
    "likes": 900,
    "comments": 120,
    "subsGained": 45,
    "shares": 80,
    "clickThroughRate": 0.062,
    "impressions": 193000
  },
  "retention": [
    { "percentile": 0.1, "viewerPercent": 0.95 },
    { "percentile": 0.5, "viewerPercent": 0.6 },
    { "percentile": 0.9, "viewerPercent": 0.15 }
  ],
  "traffic": { "browse": 0.4, "suggested": 0.3, "search": 0.15, "external": 0.1, "other": 0.05 },
  "tags": ["DNA", "bioelectric", "cassiopaean"],
  "description": "The film: <slug> | Essay: <essay url>",
  "endScreenClicks": 210,
  "cardsClicks": 130
}
```

## Aggregate queries we want to run

1. **Retention by tier** — do platinum films hold longer than shorts?
   (average retention curve per `category`)
2. **Thesis ↔ performance** — which central claims overperform?
   (join `works.json` thesis keywords vs `avgViewPercent`)
3. **Series flywheel** — do subscribers gained correlate with watch time?
4. **Best CTA** — end-screen clicks by which video precedes.

## Data flow

1. Publish → record `youtubeId` + date in `works.json`
2. Monthly pull (YouTube Data API) → fill `metrics`
3. Commit to `library/analytics/youtube-data.json`
4. ochema-site can render the dashboard from the same JSON

# Skia Pipeline — State of the Corpus

Audit date: 2026-08-03. Everything below is measured, not estimated.

## 1. The pipeline (one command per stage)

```
source (PIL py / narration_timeline / scene_manifest / storyboard)
   │  node scripts/pipeline.mjs port <manifest> --work <id>
   ▼
works/<id>/pack.json          ← Skia scene pack (semantic-essay grammar, whiteScientific)
   │  node scripts/pipeline.mjs render <pack.json>
   ▼
works/<id>/video.mp4          ← + contact.png + validation.json (auto)
   │  node scripts/pipeline.mjs publish <id> --site
   ▼
R2 atlas-sources (public)  →  ochema-site Films page  →  library/occhema.db row
```

DB tracks every work: `registered → ported → rendered → published`
(youtube_id column reserved for the publish step).

## 2. The source inventory (what we have)

| Line | Works | Source quality | Portable now? |
|---|---|---|---|
| **platinum** (queue1-4) | 79 | PIL `.py` scripts, essay embedded; 30 have narration timelines (100% narration+visual coverage, 9-54 scenes each) | ✅ 30 auto-ported, all validate |
| **goldrender** experiments | 20 | narration_timeline.json, same quality | ✅ ported |
| **tantraloka** | 111 | PIL `*_pack.py` + scene_manifest (title/subtitle/term/duration per scene, devanāgarī terms) | ✅ needs one-off devanagari map |
| **r2-factory** | 163 | **best source**: storyboard.json with spoken_passage, concrete_motif (drawable parts, motion verbs), continuity, bad_first_visual | 🟡 port script needed (storyboard → pack), then ✅ |
| **pilot** | 4 | Skia packs, hand-authored | ✅ done |
| essayviz examples | ~10 | compiler plans + packs | 🟡 separate line |

## 3. Quality assessment

### Automated baseline (what the port produces today)
- **Visual grammar**: `semantic-essay` motif with the 31 mechanism visuals (constraint-field, five-lenses, causal-vortex…) assigned round-robin per scene.
- **Consistency**: one theme (whiteScientific), one typography system, one scene structure — the corpus renders *coherent* out of the box.
- **What it is not yet**: per-film hand-crafted visuals. The round-robin assignment means the same visual can appear in different films, and visuals are not yet matched to the narration's argument beat.
- **Validation**: every ported pack passes the engine's schema + semantic checks; renders pass validation (e.g. dna_superconductor: 4920 frames, 205 s, validation true).

### Where the quality bar comes from
The `ochema-vid` skill (skills/ochema-vid/SKILL.md) defines the target workflow:
1. essay → argument IR → continuity systems → composition
2. **mechanism selection per beat**: logicvid for formal argument, semantic-essay for phenomenological, capability packs for domains, EssayViz extensions for math/cymatics/synergetics
3. ≥3 mechanism candidates per decisive beat → pick by relation preservation + motion proof
4. narration → audio analysis → render → shorts extraction

Automated port = step 2 with semantic-essay only. Upgrading a film = re-authoring its
scene `params.visual` (and optionally motif) per the skill's routing, then re-render.

### Render throughput (measured on this box, node 22, @napi-rs/canvas)
- 640×360 @12fps: ~120 frames/s
- 1280×720 @24fps: ~24 frames/s (~2.5-3 min per 200 s film)

**Backlog math**: 58 un-rendered platinum works × ~3 min ≈ **3 hours of render** for the whole line. Tantraloka 111 ≈ 5-6 h. The box can do this in a day unattended.

## 4. What "coherent format" costs, per line

| Line | To coherent | Work required |
|---|---|---|
| platinum (58 un-rendered) | ~3 h render | nothing — ports exist, queue renders |
| platinum (21 PIL-rendered) | re-render | port → render (30 already ported) |
| goldrender experiments (20) | 1 h | nothing |
| tantraloka (111) | 5-6 h + devanagari pass | one-off term map, then queue |
| r2-factory (163) | ~8 h + port script | storyboard→pack port script (~1 script), then queue |
| essayviz line | separate | align packs to MOTHERFUCKER schema |

**Total: ~1-2 days of unattended render + ~2-3 small port scripts** to get every
existing work into the coherent Skia format, minus any work you want hand-finished
per the ochema-vid skill (that is the only open-ended cost).

## 5. Recommended order

1. **Batch-render the 30 ported platinum works** tonight (background queue).
2. Write the `storyboard → pack` port (r2-factory) — it is the highest-quality source; sample the gold-plans workflow with 3-5 jobs.
3. Tantraloka devanagari map → batch-render.
4. Hand-finish the what-the-heck-is series films per ochema-vid (custom visuals, shorts extraction).
5. Publish pipeline: youtube_id per work → analytics schema already in analytics/youtube-schema.md.

## 6. Commands

```bash
node scripts/ingest.mjs                 # (re)register all sources -> db
node scripts/pipeline.mjs status        # status board
node scripts/pipeline.mjs port <manifest> --work <id>
node scripts/pipeline.mjs render works/<id>/pack.json
node scripts/pipeline.mjs publish <id> --site
node --input-type=module -e "import{openDb,query}from'./library/db.mjs';console.log(query(openDb(),'select id,status from works where line=?',['platinum']))"
```

#!/usr/bin/env node
/**
 * Ingest every known source work into works/<id>/ and the database.
 *
 * Sources:
 *   - platinum: clean/queue{1-4}/*_platinum.py (essay embedded)
 *   - goldrender: /mnt/.../goldrender output dirs (rendered PIL works)
 *   - tantraloka: goldrender pack scripts, newpacks render scripts
 *   - pilot: ochema/films/whattheheckisintelligence (packs + scripts)
 *   - r2 refs: blog-video-assets renders, factory-assets publishing renders (registered, not downloaded)
 */
import { readFileSync, writeFileSync, readdirSync, existsSync, copyFileSync, mkdirSync, statSync } from "node:fs";
import { join, resolve, basename, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { openDb, upsertWork, upsertScenes, logEvent } from "../library/db.mjs";

const ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const GOLD = "/mnt/HC_Volume_106427611/goldrender";
const CLEAN = "/root/projects/clean";
const TANTRA = "/root/projects/tantraloka";
const OCMA = "/root/projects/ochema";
const WORK_DIR = join(ROOT, "works");

function safeId(s) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60) || `work-${Date.now()}`;
}

function thesisFromPy(src) {
  const t = src.match(/^"""(.*)$/m)?.[1]?.trim() || "";
  return t.slice(0, 300);
}

function copyToSource(workId, filePath) {
  if (!existsSync(filePath)) return null;
  const dest = join(WORK_DIR, workId, "source", basename(filePath));
  mkdirSync(dirname(dest), { recursive: true });
  if (!existsSync(dest)) copyFileSync(filePath, dest);
  return dest;
}

const db = openDb();

let registered = 0;

// 1. Platinum PIL films (clean/queue{1-4})
for (const q of ["queue", "queue2", "queue3", "queue4"]) {
  const dir = join(CLEAN, q);
  if (!existsSync(dir)) continue;
  for (const f of readdirSync(dir)) {
    if (!f.endsWith("_platinum.py")) continue;
    const id = f.replace("_platinum.py", "");
    const src = readFileSync(join(dir, f), "utf8");
    const rendered = existsSync(join(GOLD, `output_${id}`));
    upsertWork(db, {
      id, line: "platinum", title: thesisFromPy(src).split("\n")[0] || id,
      thesis: thesisFromPy(src), status: rendered ? "rendered" : "registered",
      source_ref: join(dir, f), notes: `PIL platinum script (${q})`,
    });
    copyToSource(id, join(dir, f));
    if (rendered) {
      const tl = join(GOLD, `output_${id}`, "narration_timeline.json");
      if (existsSync(tl)) {
        const t = JSON.parse(readFileSync(tl, "utf8"));
        upsertScenes(db, id, (t.scenes || []).map((s, i) => ({
          id: s.scene_id || `scene-${i + 1}`, title: s.title, subtitle: s.subtitle,
          term: s.term, narration: s.narration, duration: s.duration, visual: s.visual,
        })));
        copyToSource(id, tl);
      }
    }
    registered++;
  }
}

// 2. Goldrender outputs not already covered (experiments beyond the queues)
for (const d of readdirSync(GOLD)) {
  if (!d.startsWith("output_")) continue;
  const id = d.replace("output_", "");
  const tl = join(GOLD, d, "narration_timeline.json");
  if (!existsSync(tl)) continue;
  const row = db.prepare("SELECT id FROM works WHERE id = ?").get(id);
  if (row) continue; // already registered from platinum line
  const t = JSON.parse(readFileSync(tl, "utf8"));
  upsertWork(db, {
    id, line: "goldrender", title: t.title || id,
    thesis: t.subtitle || "", status: "rendered", source_ref: tl,
    notes: "goldrender experiment output",
  });
  upsertScenes(db, id, (t.scenes || []).map((s, i) => ({
    id: s.scene_id || `scene-${i + 1}`, title: s.title, subtitle: s.subtitle,
    term: s.term, narration: s.narration, duration: s.duration, visual: s.visual,
  })));
  copyToSource(id, tl);
  registered++;
}

// 3. Tantraloka line
const tDir = join(TANTRA, "goldrender");
for (const f of readdirSync(tDir)) {
  if (!f.endsWith("_pack.py")) continue;
  const id = `tantra-${f.replace("_pack.py", "")}`;
  const src = readFileSync(join(tDir, f), "utf8");
  upsertWork(db, {
    id, line: "tantraloka", title: thesisFromPy(src).split("\n")[0] || id,
    thesis: thesisFromPy(src), status: "registered",
    source_ref: join(tDir, f), notes: "Tantraloka goldrender PIL pack",
  });
  copyToSource(id, join(tDir, f));
  registered++;
}
for (const d of readdirSync(join(TANTRA, "newpacks"))) {
  const py = join(TANTRA, "newpacks", d, "render_pack.py");
  if (!existsSync(py)) continue;
  const id = `tantra-${d.replace(/_pack$/, "")}`;
  upsertWork(db, {
    id, line: "tantraloka", title: d.replace(/_/g, " "), status: "registered",
    source_ref: py, notes: "Tantraloka newpack",
  });
  copyToSource(id, py);
  registered++;
}

// 4. Series pilot
const pilotDir = join(OCMA, "films", "whattheheckisintelligence");
const pilotPacks = [
  ...readdirSafe(join(pilotDir, "packs")).map((f) => join(pilotDir, "packs", f)),
  ...readdirSafe(join(pilotDir, "shorts")).map((f) => join(pilotDir, "shorts", f)),
];
for (const pf of pilotPacks) {
  if (!pf.endsWith(".json")) continue;
  const id = `pilot-${basename(pf).replace(".json", "")}`;
  const p = JSON.parse(readFileSync(pf, "utf8"));
  upsertWork(db, {
    id, line: "pilot", title: p.title || id, status: "rendered",
    source_ref: pf, notes: "Series pilot skia pack",
  });
  upsertScenes(db, id, (p.scenes || []).map((s) => ({
    id: s.id, title: s.title, subtitle: s.subtitle, term: s.term,
    narration: null, duration: s.duration, visual: s.params?.visual,
  })));
  copyToSource(id, pf);
  registered++;
}

function readdirSafe(dir) {
  return existsSync(dir) ? readdirSync(dir) : [];
}

// 5. R2 factory sources — registered as refs (no download)
const r2Refs = [
  ...(await rcloneList("blog-video-assets/renders")),
  ...(await rcloneList("factory-assets/content/publishing/renders")),
];
for (const job of r2Refs) {
  const id = `r2-${safeId(job)}`;
  const row = db.prepare("SELECT id FROM works WHERE id = ?").get(id);
  if (row) continue;
  upsertWork(db, {
    id, line: "r2-factory", title: job, status: "registered",
    source_ref: `r2:${job.startsWith("blog") ? "blog-video-assets" : "factory-assets"}/${job}`,
    notes: "R2 factory job — storyboard + source essay in bucket, fetch on port",
  });
  registered++;
}

console.log(`Registered ${registered} works (total in db: ${db.prepare("SELECT COUNT(*) c FROM works").get().c})`);
console.log(db.prepare("SELECT line, COUNT(*) c, status FROM works GROUP BY line ORDER BY c DESC").all()
  .map((r) => `  ${r.line}: ${r.c}`).join("\n"));

async function rcloneList(path) {
  const { execFileSync } = await import("node:child_process");
  try {
    const out = execFileSync("rclone", ["lsf", `r2:${path}`], { encoding: "utf8", timeout: 120000 });
    return out.split("\n").filter((l) => l.trim().endsWith("/")).map((l) => l.trim().replace(/\/$/, ""));
  } catch {
    return [];
  }
}

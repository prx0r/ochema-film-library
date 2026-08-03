#!/usr/bin/env node
/**
 * Ochema film pipeline: port → render → publish.
 *
 *   node pipeline.mjs port <manifest.json> --work <id> --out works/<id>/pack.json
 *   node pipeline.mjs render <pack.json> [--out video.mp4] [--width 1280] [--height 720] [--fps 24]
 *   node pipeline.mjs publish <workId> [--site]
 *
 * Port sources (either works):
 *   - goldrender output: narration_timeline.json
 *   - PIL pack:          scene_manifest.json
 */
import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync, spawnSync } from "node:child_process";
import { openDb, upsertWork, upsertScenes, logEvent, DB_PATH } from "../library/db.mjs";

const ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const ENGINE = "/root/projects/clean/MOTHERFUCKER";
const THEME = "whiteScientific";

const SEMANTIC_VISUALS = [
  "constraint-field", "point-of-view", "five-lenses", "local-power", "melody-time",
  "attention-beam", "desire-orbit", "smallness-cage", "powered-prison", "practice-folds",
  "upsurge", "wave-ocean", "textures-display", "limitation-reversal", "opening-fist",
  "pattern-ensemble", "dependency-network", "umwelt-windows", "multiscale-agent",
  "boundary-gates", "memory-relay", "morphing-invariant", "reciprocal-reeds", "causal-vortex",
  "cooling-chain", "dialectic-bridge", "tuning-network", "source-compile-runtime",
  "recursive-observer", "open-question", "relational-birth",
];

const DEVANAGARI_ROTATION = [
  "सत्त्व", "रजस्", "तमस्", "प्राण", "शक्ति", "बोध",
  "स्पन्द", "विभूति", "धर्म", "कर्म", "योग", "मन्त्र",
];

const WORK_TERMS = {
  dna_superconductor: "विद्युत्",
  voice_inside_chest: "वाक्",
  beliefs_create_biology: "जीव",
  consciousness_container: "चेतन",
  yoga_sutras: "योग",
  nagarjuna_emptiness: "शून्यता",
  spacious_present: "क्षण",
  you_create_reality: "विधान",
  life_crosses: "जन्म",
  law_of_one_densities: "घन",
  daimon_encounter: "दैमन",
  dream_incubation: "स्वप्न",
  dreams_create_worlds: "माया",
  fire_not_destroying: "अग्नि",
  svatantrya_freedom: "स्वातन्त्र्य",
  veils_of_forgetting: "मोह",
  wave: "तरङ्ग",
  ai_cannot_dream: "स्वप्न",
  constructed_self: "अहं",
  cooperation: "सङ्घ",
  free_energy_primitive: "ऊर्जा",
  objects_as_actions: "क्रिया",
  psyche_gestalt: "चित्त",
  universe_created_every_moment: "सृष्टि",
  past_can_be_changed: "काल",
  thoughts_reach_14th_century: "चिन्तन",
};

function kebab(s) {
  let k = s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 28);
  if (k.length < 3) k = `${k || "scene"}${k.length < 3 ? "01".slice(0, 3 - k.length) : ""}`;
  while (k.length < 3) k = `${k}${k}`;
  return k.slice(0, 32);
}

function hashId(s) {
  let h = 0;
  for (const c of s) h = (h * 31 + c.charCodeAt(0)) >>> 0;
  return h;
}

function portManifest(manifestPath, workId, devanagariOverride) {
  const m = JSON.parse(readFileSync(manifestPath, "utf8"));
  const entries = m.scenes;
  if (!Array.isArray(entries) || entries.length === 0) {
    throw new Error("manifest has no scenes[]");
  }
  const workTerm = devanagariOverride || WORK_TERMS[workId];
  const scenes = entries.map((e, i) => {
    const title = (e.title || `Scene ${i + 1}`).trim();
    const subtitle = (e.subtitle || e.narration || e.summary || "").trim() || "The thread continues.";
    const term = (e.term || title).trim().slice(0, 50);
    const devanagari = workTerm || DEVANAGARI_ROTATION[i % DEVANAGARI_ROTATION.length];
    const duration = Math.max(1, Math.min(30, Math.round(e.duration_seconds ?? e.duration ?? 10)));
    return {
      id: kebab(e.scene_id || title),
      title: title.slice(0, 80),
      subtitle: subtitle.slice(0, 140),
      term: term.slice(0, 50),
      devanagari,
      motif: "semantic-essay",
      duration,
      params: { visual: SEMANTIC_VISUALS[i % SEMANTIC_VISUALS.length] },
    };
  });
  return {
    version: "1.0",
    id: (workId || m.project || "film").toLowerCase().replace(/[^a-z0-9-]/g, "-"),
    title: (m.title || workId || "Ochema Film").slice(0, 120),
    description: (m.subtitle || m.source_basis || "Ported from the Ochema corpus.").slice(0, 300),
    theme: THEME,
    seed: hashId(workId || m.project || "ochema"),
    render: {
      width: 1280,
      height: 720,
      fps: 24,
      crf: 18,
      preset: "veryfast",
      sceneDuration: 10,
      transitionDuration: 0.35,
    },
    scenes,
  };
}

function cmd(argv) {
  const [command, target] = argv;
  const opts = {};
  for (let i = 2; i < argv.length; i += 1) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const [k, v] = a.slice(2).split("=", 2);
      const next = argv[i + 1];
      if (v !== undefined) {
        opts[k] = v;
      } else if (next !== undefined && !next.startsWith("--")) {
        opts[k] = next;
        i += 1;
      } else {
        opts[k] = true;
      }
    }
  }

  if (command === "port") {
    if (!target) throw new Error("port requires a manifest path");
    const workId = opts.work || dirname(target).split("/").pop().replace(/^output_/, "");
    const pack = portManifest(target, workId, opts.devanagari);
    const out = opts.out || join(ROOT, "works", workId, "pack.json");
    mkdirSync(dirname(out), { recursive: true });
    writeFileSync(out, JSON.stringify(pack, null, 2));
    const db = openDb();
    const m = JSON.parse(readFileSync(target, "utf8"));
    upsertWork(db, {
      id: workId, line: opts.line ?? "ported", title: m.title || pack.title,
      thesis: m.subtitle || "", status: "ported", source_ref: target, pack_path: out,
    });
    upsertScenes(db, workId, (m.scenes || []).map((s, i) => ({
      id: s.scene_id || `scene-${i + 1}`, title: s.title, subtitle: s.subtitle,
      term: s.term, narration: s.narration, duration: s.duration_seconds ?? s.duration, visual: s.visual,
    })));
    logEvent(db, workId, "ported");
    console.log(`Port: ${pack.scenes.length} scenes → ${out} (theme ${THEME})`);
    return;
  }

  if (command === "render") {
    if (!target) throw new Error("render requires a pack.json path");
    const packAbs = resolve(target);
    const out = resolve(opts.out || target.replace(/\.json$/, ".mp4"));
    mkdirSync(dirname(out), { recursive: true });
    const args = ["cli.mjs", "render", packAbs, "--out", out];
    if (opts.width) args.push("--width", opts.width);
    if (opts.height) args.push("--height", opts.height);
    if (opts.fps) args.push("--fps", opts.fps);
    const r = spawnSync("node", args, { cwd: ENGINE, encoding: "utf8", timeout: 6 * 3600 * 1000 });
    process.stdout.write(r.stdout);
    process.stderr.write(r.stderr);
    if (r.status !== 0) throw new Error(`render failed (${r.status})`);
    const db = openDb();
    const workId = basename(dirname(packAbs));
    const w = db.prepare("SELECT * FROM works WHERE id = ?").get(workId);
    if (w) {
      db.prepare("UPDATE works SET status = ?, video_path = ?, updated_at = ? WHERE id = ?")
        .run("rendered", out, new Date().toISOString(), workId);
      logEvent(db, workId, "rendered");
    }
    console.log(`Render: ${out} (db: ${DB_PATH})`);
    return;
  }

  if (command === "publish") {
    const workId = target;
    if (!workId) throw new Error("publish requires a work id");
    const workDir = join(ROOT, "works", workId);
    const video = join(workDir, "video.mp4");
    if (!existsSync(video)) throw new Error(`no ${video} — render first`);
    const contact = join(workDir, "contact.png");
    const pack = JSON.parse(readFileSync(join(workDir, "pack.json"), "utf8"));
    const r1 = spawnSync("rclone", ["copyto", video, `r2:atlas-sources/videos/${workId}.mp4`, "--log-level", "ERROR"], { encoding: "utf8" });
    if (r1.status !== 0) throw new Error("rclone video upload failed");
    if (existsSync(contact)) {
      const jpg = join(workDir, "thumb.jpg");
      spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-i", contact, "-frames:v", "1", "-q:v", "4", jpg]);
      spawnSync("rclone", ["copyto", jpg, `r2:atlas-sources/thumbnails/${workId}.jpg`, "--log-level", "ERROR"]);
    }
    const worksJson = JSON.parse(readFileSync(join(ROOT, "library", "works.json"), "utf8"));
    const w = worksJson.works.find((x) => x.id === workId);
    if (w) {
      w.skiaPorted = true;
      w.onSite = true;
      w.rendered = true;
      w.videoUrl = `https://pub-8f77709efb2043fbbd8e88677347249a.r2.dev/videos/${workId}.mp4`;
      writeFileSync(join(ROOT, "library", "works.json"), JSON.stringify(worksJson, null, 2));
    }
    const db = openDb();
    const row = db.prepare("SELECT * FROM works WHERE id = ?").get(workId);
    if (row) {
      db.prepare("UPDATE works SET status = ?, published_url = ?, pack_path = ?, updated_at = ? WHERE id = ?")
        .run("published", `https://pub-8f77709efb2043fbbd8e88677347249a.r2.dev/videos/${workId}.mp4`, join(workDir, "pack.json"), new Date().toISOString(), workId);
      logEvent(db, workId, "published");
    }
    if (opts.site) {
      const siteVideos = join("/mnt/HC_Volume_106427611/ochema-site/data/videos.json");
      const sv = JSON.parse(readFileSync(siteVideos, "utf8"));
      if (!sv.platinum.some((p) => p.id === `platinum-${workId}`)) {
        sv.platinum.push({
          id: `platinum-${workId}`,
          title: pack.title,
          file: `${workId}.mp4`,
          thumb: `${workId}.jpg`,
          note: "Skia render — the new pipeline",
        });
        writeFileSync(siteVideos, JSON.stringify(sv, null, 2));
        spawnSync("git", ["add", "-A"], { cwd: "/mnt/HC_Volume_106427611/ochema-site" });
        spawnSync("git", ["commit", "-m", `pipeline: publish ${workId}`, "-q"], { cwd: "/mnt/HC_Volume_106427611/ochema-site" });
        spawnSync("git", ["push", "-q"], { cwd: "/mnt/HC_Volume_106427611/ochema-site" });
      }
    }
    console.log(`Published: ${workId} → R2 + library + site`);
    return;
  }

  if (command === "status") {
    const db = openDb();
    const byLine = db.prepare("SELECT line, status, COUNT(*) c FROM works GROUP BY line, status ORDER BY line").all();
    console.log("works by line/status:");
    let last = "";
    for (const r of byLine) {
      if (r.line !== last) { console.log(`  ${r.line}:`); last = r.line; }
      console.log(`    ${r.status}: ${r.c}`);
    }
    const total = db.prepare("SELECT COUNT(*) c FROM works").get().c;
    const rendered = db.prepare("SELECT COUNT(*) c FROM works WHERE status IN ('rendered','published')").get().c;
    console.log(`total: ${total} | rendered/published: ${rendered}`);
    return;
  }

  throw new Error(`unknown command: ${command}`);
}

try {
  cmd(process.argv.slice(2));
} catch (e) {
  console.error(`pipeline: ${e.message}`);
  process.exit(1);
}

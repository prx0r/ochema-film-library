#!/usr/bin/env node
// Publish every rendered work to R2 + site in one pass (batch, single git push).
//   node scripts/publish-all.mjs
import { readdirSync, existsSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { openDb } from "../library/db.mjs";

const ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const WORKS = join(ROOT, "works");
const SITE = "/mnt/HC_Volume_106427611/ochema-site";
const PUBLIC = "https://pub-8f77709efb2043fbbd8e88677347249a.r2.dev";

const db = openDb();
const pending = [];

for (const id of readdirSync(WORKS)) {
  const dir = join(WORKS, id);
  const video = join(dir, "video.mp4");
  if (!existsSync(video) || statSync(video).size < 1e6) continue;
  const row = db.prepare("SELECT status FROM works WHERE id = ?").get(id);
  if (row && row.status === "published") continue;
  pending.push(id);
}

console.log(`Publishing ${pending.length} works…`);
const siteVideos = JSON.parse(
  (await import("node:fs")).readFileSync(join(SITE, "data", "videos.json"), "utf8")
);
let added = 0;

for (const id of pending) {
  const dir = join(WORKS, id);
  const video = join(dir, "video.mp4");
  const contact = join(dir, "contact.png");
  const packPath = join(dir, "pack.json");
  let title = id;
  try {
    const pack = JSON.parse((await import("node:fs")).readFileSync(packPath, "utf8"));
    title = pack.title || id;
  } catch {}
  const up = spawnSync("rclone", ["copyto", video, `r2:atlas-sources/videos/${id}.mp4`, "--log-level", "ERROR"]);
  if (up.status !== 0) { console.log(`  ✗ ${id} rclone failed`); continue; }
  if (existsSync(contact)) {
    const jpg = join(dir, "thumb.jpg");
    spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-i", contact, "-frames:v", "1", "-q:v", "4", jpg]);
    spawnSync("rclone", ["copyto", jpg, `r2:atlas-sources/thumbnails/${id}.jpg`, "--log-level", "ERROR"]);
  }
  if (!siteVideos.platinum.some((p) => p.id === `platinum-${id}`)) {
    siteVideos.platinum.push({
      id: `platinum-${id}`, title, file: `${id}.mp4`,
      thumb: `${id}.jpg`, note: "Skia render — unified pipeline",
    });
    added++;
  }
  const row = db.prepare("SELECT * FROM works WHERE id = ?").get(id);
  if (row) {
    db.prepare("UPDATE works SET status = ?, published_url = ?, updated_at = ? WHERE id = ?")
      .run("published", `${PUBLIC}/videos/${id}.mp4`, new Date().toISOString(), id);
    db.prepare("INSERT INTO events (work_id, event, at) VALUES (?, ?, ?)")
      .run(id, "published", new Date().toISOString());
  }
  console.log(`  ✓ ${id}`);
}

if (added > 0) {
  (await import("node:fs")).writeFileSync(join(SITE, "data", "videos.json"), JSON.stringify(siteVideos, null, 2));
  spawnSync("git", ["add", "-A"], { cwd: SITE });
  spawnSync("git", ["commit", "-m", `pipeline: publish ${pending.length} skia renders`, "-q"], { cwd: SITE });
  const push = spawnSync("git", ["push", "-q"], { cwd: SITE });
  console.log(push.status === 0 ? "Site pushed." : "Site push failed (check git state).");
}
console.log("publish-all complete.");

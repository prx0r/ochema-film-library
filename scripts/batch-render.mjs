#!/usr/bin/env node
// Batch-render all ported works that don't have a video yet.
//   node scripts/batch-render.mjs [--limit N] [--only <line>]
import { readdirSync, existsSync, unlinkSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const WORKS = join(ROOT, "works");

const argv = process.argv.slice(2);
const limit = argv.includes("--limit") ? Number(argv[argv.indexOf("--limit") + 1]) : Infinity;
const only = argv.includes("--only") ? argv[argv.indexOf("--only") + 1] : null;

const queue = [];
for (const id of readdirSync(WORKS)) {
  const dir = join(WORKS, id);
  if (!existsSync(join(dir, "pack.json"))) continue;
  if (existsSync(join(dir, "video.mp4"))) continue;
  queue.push(id);
}
if (only) queue.splice(queue.indexOf(only), 1), queue.unshift(only);
const jobs = queue.slice(0, limit);

console.log(`Batch: ${jobs.length} works to render (${queue.length - jobs.length} skipped)`);

let i = 0;
for (const id of jobs) {
  i++;
  console.log(`[${i}/${jobs.length}] rendering ${id}…`);
  const r = await new Promise((res) => {
    const p = spawn("node", [
      "scripts/pipeline.mjs", "render",
      join(WORKS, id, "pack.json"),
      "--out", join(WORKS, id, "video.mp4"),
    ], { cwd: ROOT, stdio: ["ignore", "inherit", "inherit"] });
    p.on("exit", (code) => res(code));
  });
  if (r !== 0) { console.log(`  ✗ ${id} failed`); unlinkSync(join(WORKS, id, "video.mp4")); continue; }
  console.log(`  ✓ ${id}`);
}
console.log("Batch complete.");

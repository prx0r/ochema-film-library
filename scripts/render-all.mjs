#!/usr/bin/env node
// Orchestrator: wait for an existing batch (optional PID arg), keep re-rendering
// until nothing is pending, then publish everything to R2 + the site.
//   node scripts/render-all.mjs [existing-batch-pid]
import { spawn, execSync } from "node:child_process";
import { readdirSync, existsSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const WORKS = join(ROOT, "works");
const waitPid = process.argv[2];

function alive(pid) {
  try { execSync(`kill -0 ${pid} 2>/dev/null`); return true; } catch { return false; }
}

function pendingCount() {
  let n = 0;
  for (const id of readdirSync(WORKS)) {
    if (existsSync(join(WORKS, id, "pack.json")) && !existsSync(join(WORKS, id, "video.mp4"))) n++;
  }
  return n;
}

console.log(`[orchestrator] start. waiting-for=${waitPid ?? "none"} pending=${pendingCount()}`);

if (waitPid && alive(waitPid)) {
  console.log(`[orchestrator] waiting for existing batch (pid ${waitPid})…`);
  while (alive(waitPid)) execSync("sleep 20");
  console.log("[orchestrator] existing batch done.");
}

const MAX_PASSES = 3;
for (let pass = 1; pass <= MAX_PASSES; pass++) {
  const pending = pendingCount();
  if (pending === 0) break;
  console.log(`[orchestrator] pass ${pass}/${MAX_PASSES}: ${pending} works pending`);
  const r = await new Promise((res) => {
    const p = spawn("node", ["scripts/batch-render.mjs"], { cwd: ROOT, stdio: "inherit" });
    p.on("exit", (code) => res(code));
  });
  if (r !== 0) console.log(`[orchestrator] batch pass ${pass} exited ${r}`);
}

console.log("[orchestrator] rendering complete. publishing…");
const pub = await new Promise((res) => {
  const p = spawn("node", ["scripts/publish-all.mjs"], { cwd: ROOT, stdio: "inherit" });
  p.on("exit", (code) => res(code));
});
console.log(`[orchestrator] done (publish exit ${pub}).`);

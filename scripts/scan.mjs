import { readFileSync, writeFileSync, readdirSync, existsSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");

const LINES = {
  platinumFilms: { dir: "/root/projects/clean", match: (n) => n.endsWith("_platinum.py"), maxDepth: 4 },
  tantralokaScripts: { dir: "/root/projects/tantraloka", match: (n) => /\.(py|mjs|js)$/.test(n), maxDepth: 6 },
  essayvizEngine: { dir: "/root/projects/essayviz-workspace", match: (n) => /\.(mjs|js|py)$/.test(n), maxDepth: 6 },
  blogFactory: { dir: "/root/projects/blog", match: (n) => /\.(mjs|js|py)$/.test(n), maxDepth: 6 },
  fatherfuckerSnapshots: { dir: "/root/projects/clean/FATHERFUCKER", match: (n) => /\.(py|mjs)$/.test(n), maxDepth: 8 },
  ochemaFilms: { dir: "/root/projects/ochema/films", match: (n) => /\.(json|mjs|mp4|png)$/.test(n), maxDepth: 5 },
  goldrenderOutputs: { dir: "/mnt/HC_Volume_106427611/goldrender", match: (n) => /\.(mp4|json)$/.test(n) || n.endsWith("_pack.py"), maxDepth: 4 },
  goldrenderTantraloka: { dir: "/root/projects/tantraloka/goldrender", match: (n) => /\.(mp4|py)$/.test(n), maxDepth: 3 },
};

function walk(dir, depth, maxDepth, match, out) {
  if (depth > maxDepth || !existsSync(dir)) return;
  let entries;
  try { entries = readdirSync(dir); } catch { return; }
  for (const name of entries) {
    if (name.startsWith(".") || name === "node_modules" || name === "__pycache__" || name === "node_modules" || name === ".next") continue;
    const p = join(dir, name);
    let st;
    try { st = statSync(p); } catch { continue; }
    if (st.isDirectory()) walk(p, depth + 1, maxDepth, match, out);
    else if (match(name)) out.push({ path: p, bytes: st.size, mtime: st.mtime.toISOString() });
  }
}

const catalog = { generated: new Date().toISOString(), lines: {} };
for (const [name, spec] of Object.entries(LINES)) {
  const files = [];
  walk(spec.dir, 0, spec.maxDepth, spec.match, files);
  catalog.lines[name] = {
    dir: spec.dir,
    count: files.length,
    bytes: files.reduce((s, f) => s + f.bytes, 0),
    files,
  };
}

writeFileSync(join(ROOT, "library", "index.json"), JSON.stringify(catalog, null, 2));
for (const [name, line] of Object.entries(catalog.lines)) {
  console.log(`${name}: ${line.count} files, ${(line.bytes / 1e6).toFixed(0)} MB`);
}

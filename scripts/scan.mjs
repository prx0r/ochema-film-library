import { readdirSync, existsSync, statSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");

const SITES = {
  platinumPIL: "/root/projects/clean",
  goldrenderVolume: "/mnt/HC_Volume_106427611/goldrender",
  goldrenderTantraloka: "/root/projects/tantraloka/goldrender",
  essayvizArchive: "/root/projects/ochema/EssayViz",
  essayvizWorkspace: "/root/projects/essayviz-workspace",
  ochemaFilms: "/root/projects/ochema/films",
  ochemaSkills: "/root/projects/ochema/skills",
  tantralokaVids: "/root/projects/tantraloka/vids",
  tantralokaNewpacks: "/root/projects/tantraloka/newpacks",
};

function walk(dir, depth, maxDepth, out, filter) {
  if (depth > maxDepth || !existsSync(dir)) return;
  for (const name of readdirSync(dir)) {
    if (name.startsWith(".") || name === "node_modules" || name === "__pycache__") continue;
    const p = join(dir, name);
    let st;
    try { st = statSync(p); } catch { continue; }
    if (st.isDirectory()) {
      walk(p, depth + 1, maxDepth, out, filter);
    } else if (filter(name)) {
      out.push({ path: p, size: st.size, mtime: st.mtime.toISOString() });
    }
  }
}

const catalog = { generated: new Date().toISOString(), sites: {} };

for (const [site, dir] of Object.entries(SITES)) {
  const files = [];
  const filters = {
    platinumPIL: (n) => n.endsWith(".py"),
    goldrenderVolume: (n) => /\.(mp4|zip)$/.test(n) || n.endsWith("_pack.py") || /\.(jpg|png)$/.test(n) && n.includes("contact"),
    goldrenderTantraloka: (n) => /\.(mp4|zip)$/.test(n) || n.endsWith(".py"),
    essayvizArchive: (n) => /\.(zip|tgz|pdf|epub)$/.test(n),
    essayvizWorkspace: (n) => /\.(mjs|js|json|py|mp4)$/.test(n),
    ochemaFilms: (n) => /\.(mp4|json|mjs|png)$/.test(n),
    ochemaSkills: (n) => n.endsWith(".md"),
    tantralokaVids: (n) => n.endsWith(".zip"),
    tantralokaNewpacks: (n) => /\.(mp4|zip)$/.test(n),
  };
  walk(dir, 0, 4, files, filters[site]);
  catalog.sites[site] = {
    dir,
    fileCount: files.length,
    totalBytes: files.reduce((s, f) => s + f.size, 0),
    files,
  };
}

const fs = await import("node:fs");
fs.writeFileSync(join(ROOT, "library", "index.json"), JSON.stringify(catalog, null, 2));
for (const [site, s] of Object.entries(catalog.sites)) {
  console.log(`${site}: ${s.fileCount} files, ${(s.totalBytes / 1e9).toFixed(2)} GB`);
}

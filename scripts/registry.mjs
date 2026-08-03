import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const GOLDRENDER = "/mnt/HC_Volume_106427611/goldrender";
const QUEUES = ["queue", "queue2", "queue3", "queue4"];
const CLEAN = "/root/projects/clean";

const works = [];
for (const q of QUEUES) {
  const dir = join(CLEAN, q);
  if (!existsSync(dir)) continue;
  for (const f of readdirSync(dir)) {
    if (!f.endsWith("_platinum.py")) continue;
    const id = f.replace("_platinum.py", "");
    const src = readFileSync(join(dir, f), "utf8");
    const title = src.match(/^"""(.*)$/m)?.[1]?.trim() || id;
    const thesis = src.match(/FILM THESIS\s*-+\s*\n([\s\S]*?)(?=\n-{3,}|\n[A-Z ]{5,}\n|$)/)?.[1]
      ?.split("\n").map((l) => l.trim()).filter(Boolean).slice(0, 4).join(" ")
      || "";
    const rendered = existsSync(join(GOLDRENDER, `output_${id}`));
    works.push({
      id,
      queue: q,
      title,
      thesis: thesis.slice(0, 300),
      pil: `queue/${q}/${f}`,
      rendered,
      skiaPorted: false,
      onSite: false,
      youtubeStatus: "unpublished",
    });
  }
}

works.sort((a, b) => a.id.localeCompare(b.id));
writeFileSync(join(ROOT, "library", "works.json"), JSON.stringify({ generated: new Date().toISOString(), count: works.length, works }, null, 2));
console.log(`Registry: ${works.length} works (${works.filter((w) => w.rendered).length} rendered)`);
for (const w of works) {
  if (w.rendered) console.log(`  RENDERED  ${w.id}`);
}

import { DatabaseSync } from "node:sqlite";
import { mkdirSync } from "node:fs";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(fileURLToPath(new URL(".", import.meta.url)), "..");
const DB_PATH = join(ROOT, "library", "occhema.db");

export function openDb() {
  const db = new DatabaseSync(DB_PATH);
  db.exec(`
    CREATE TABLE IF NOT EXISTS works (
      id TEXT PRIMARY KEY,
      title TEXT,
      thesis TEXT,
      line TEXT,
      status TEXT DEFAULT 'registered',
      source_ref TEXT,
      pack_path TEXT,
      video_path TEXT,
      youtube_id TEXT,
      published_url TEXT,
      notes TEXT,
      created_at TEXT,
      updated_at TEXT
    );
    CREATE TABLE IF NOT EXISTS scenes (
      work_id TEXT,
      scene_id TEXT,
      title TEXT,
      subtitle TEXT,
      term TEXT,
      narration TEXT,
      duration REAL,
      visual TEXT,
      PRIMARY KEY (work_id, scene_id)
    );
    CREATE TABLE IF NOT EXISTS events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      work_id TEXT,
      event TEXT,
      at TEXT
    );
  `);
  return db;
}

export function upsertWork(db, work) {
  const now = new Date().toISOString();
  const existing = db.prepare("SELECT updated_at FROM works WHERE id = ?").get(work.id);
  db.prepare(`
    INSERT INTO works (id, title, thesis, line, status, source_ref, pack_path, video_path, youtube_id, published_url, notes, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
      title=excluded.title, thesis=excluded.thesis, line=excluded.line,
      status=excluded.status, source_ref=excluded.source_ref,
      pack_path=excluded.pack_path, video_path=excluded.video_path,
      youtube_id=excluded.youtube_id, published_url=excluded.published_url,
      notes=excluded.notes, updated_at=excluded.updated_at
  `).run(
    work.id, work.title ?? null, work.thesis ?? null, work.line ?? null,
    work.status ?? "registered", work.source_ref ?? null,
    work.pack_path ?? null, work.video_path ?? null,
    work.youtube_id ?? null, work.published_url ?? null,
    work.notes ?? null, existing?.updated_at ?? now, now
  );
}

export function logEvent(db, workId, event) {
  db.prepare("INSERT INTO events (work_id, event, at) VALUES (?, ?, ?)").run(
    workId, event, new Date().toISOString()
  );
}

export function upsertScenes(db, workId, scenes) {
  const del = db.prepare("DELETE FROM scenes WHERE work_id = ?");
  const ins = db.prepare(`
    INSERT OR REPLACE INTO scenes (work_id, scene_id, title, subtitle, term, narration, duration, visual)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  db.exec("BEGIN");
  try {
    del.run(workId);
    for (const s of scenes) {
      ins.run(workId, s.id ?? null, s.title ?? null, s.subtitle ?? null, s.term ?? null, s.narration ?? null, s.duration ?? null, s.visual ?? null);
    }
    db.exec("COMMIT");
  } catch (e) {
    db.exec("ROLLBACK");
    throw e;
  }
}

export function query(db, sql, params = []) {
  return db.prepare(sql).all(...params);
}

export { DB_PATH };

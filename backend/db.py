"""SQLite 数据库操作"""
import os
import aiosqlite

DB_PATH = os.environ.get("JOB_DB_PATH", os.path.join(os.path.dirname(__file__), "job_assistant.db"))

_pool = None


async def get_db():
    global _pool
    if _pool is None:
        _pool = await aiosqlite.connect(DB_PATH)
        _pool.row_factory = aiosqlite.Row
        await _pool.execute("PRAGMA journal_mode=WAL")
    return _pool


async def close_db():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def init_db():
    db = await get_db()
    await db.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL DEFAULT '',
            position TEXT NOT NULL DEFAULT '',
            salary TEXT DEFAULT '',
            location TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT '待投',
            link TEXT DEFAULT '',
            note TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(app_id) REFERENCES applications(id) ON DELETE CASCADE
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS resume_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL DEFAULT '{}'
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL DEFAULT ''
        )
    """)
    await db.execute("CREATE INDEX IF NOT EXISTS idx_app_status ON applications(status)")
    await db.execute("CREATE INDEX IF NOT EXISTS idx_msg_app ON messages(app_id)")
    await db.commit()


async def add_application(data: dict) -> int:
    db = await get_db()
    cur = await db.execute(
        """INSERT INTO applications (company, position, salary, location, status, link, note)
           VALUES (?,?,?,?,?,?,?)""",
        (data.get("company", ""), data.get("position", ""), data.get("salary", ""),
         data.get("location", ""), data.get("status", "待投"), data.get("link", ""), data.get("note", ""))
    )
    await db.commit()
    return cur.lastrowid


async def update_application_status(id: int, status: str):
    db = await get_db()
    await db.execute("UPDATE applications SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (status, id))
    await db.commit()


async def list_applications(status: str | None = None, keyword: str | None = None) -> list[dict]:
    db = await get_db()
    sql = "SELECT * FROM applications WHERE 1=1"
    params = []
    if status:
        sql += " AND status=?"
        params.append(status)
    if keyword:
        sql += " AND (company LIKE ? OR position LIKE ?)"
        kw = f"%{keyword}%"
        params.extend([kw, kw])
    sql += " ORDER BY updated_at DESC"
    cur = await db.execute(sql, params)
    rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def delete_application(id: int):
    db = await get_db()
    await db.execute("DELETE FROM messages WHERE app_id=?", (id,))
    await db.execute("DELETE FROM applications WHERE id=?", (id,))
    await db.commit()


async def add_message(app_id: int, role: str, content: str):
    db = await get_db()
    await db.execute("INSERT INTO messages (app_id, role, content) VALUES (?,?,?)", (app_id, role, content))
    await db.commit()


async def get_messages(app_id: int) -> list[dict]:
    db = await get_db()
    cur = await db.execute("SELECT * FROM messages WHERE app_id=? ORDER BY created_at", (app_id,))
    return [dict(r) for r in await cur.fetchall()]


async def save_template(name: str, content: str):
    db = await get_db()
    await db.execute("INSERT INTO templates (name, content) VALUES (?,?)", (name, content))
    await db.commit()


async def list_templates() -> list[dict]:
    db = await get_db()
    cur = await db.execute("SELECT * FROM templates ORDER BY created_at DESC")
    return [dict(r) for r in await cur.fetchall()]


async def delete_template(id: int):
    db = await get_db()
    await db.execute("DELETE FROM templates WHERE id=?", (id,))
    await db.commit()


async def save_resume_info(data: dict):
    import json
    db = await get_db()
    await db.execute("DELETE FROM resume_info")
    await db.execute("INSERT INTO resume_info (data) VALUES (?)", (json.dumps(data, ensure_ascii=False),))
    await db.commit()


async def get_resume_info() -> dict | None:
    import json
    db = await get_db()
    cur = await db.execute("SELECT data FROM resume_info ORDER BY id DESC LIMIT 1")
    row = await cur.fetchone()
    return json.loads(row[0]) if row else None


async def get_setting(key: str) -> str | None:
    db = await get_db()
    cur = await db.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = await cur.fetchone()
    return row[0] if row else None


async def set_setting(key: str, value: str):
    db = await get_db()
    await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
    await db.commit()


async def get_application_stats() -> dict:
    db = await get_db()
    total = await db.execute("SELECT COUNT(*) FROM applications")
    total = (await total.fetchone())[0]
    by_status = await db.execute(
        "SELECT status, COUNT(*) as cnt FROM applications GROUP BY status"
    )
    by_status = {r["status"]: r["cnt"] for r in await by_status.fetchall()}
    by_company = await db.execute(
        "SELECT company, COUNT(*) as cnt FROM applications GROUP BY company ORDER BY cnt DESC LIMIT 10"
    )
    by_company = [dict(r) for r in await by_company.fetchall()]
    by_date = await db.execute(
        "SELECT DATE(created_at) as date, COUNT(*) as cnt FROM applications GROUP BY DATE(created_at) ORDER BY date DESC LIMIT 30"
    )
    by_date = [dict(r) for r in await by_date.fetchall()]
    return {"total": total, "by_status": by_status, "by_company": by_company, "by_date": by_date}

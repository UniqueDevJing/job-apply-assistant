"""简历投递助手 - 后端服务"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from db import (
    init_db, add_application, update_application_status, list_applications, delete_application,
    add_message, get_messages, save_template, list_templates, delete_template,
    save_resume_info, get_resume_info, get_application_stats,
    set_setting, get_setting,
)
from ai import generate_reply, test_ai_connection
from resume_parser import parse_resume
import os
import shutil
import tempfile

app = FastAPI(title="Job Apply Assistant", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# ============ 投递管理 ============

@app.post("/api/applications")
async def create_application(data: dict):
    id = await add_application(data)
    return {"id": id, "status": "ok"}


@app.get("/api/applications")
async def get_applications(status: str = None, keyword: str = None):
    apps = await list_applications(status, keyword)
    return {"applications": apps}


@app.put("/api/applications/{id}/status")
async def change_status(id: int, data: dict):
    await update_application_status(id, data["status"])
    return {"status": "ok"}


@app.delete("/api/applications/{id}")
async def remove_application(id: int):
    await delete_application(id)
    return {"status": "ok"}


# ============ 消息管理 ============

@app.post("/api/applications/{app_id}/messages")
async def add_msg(app_id: int, data: dict):
    await add_message(app_id, data["role"], data["content"])
    return {"status": "ok"}


@app.get("/api/applications/{app_id}/messages")
async def get_msgs(app_id: int):
    msgs = await get_messages(app_id)
    return {"messages": msgs}


# ============ AI 回复 ============

@app.post("/api/ai/reply")
async def ai_reply(data: dict):
    replies = await generate_reply(
        data.get("hr_message", ""),
        data.get("company", ""),
        data.get("position", ""),
    )
    return {"replies": replies}


@app.post("/api/ai/test")
async def test_ai(data: dict):
    ok = await test_ai_connection(data.get("provider", "ollama"))
    return {"ok": ok}


# ============ 模板管理 ============

@app.post("/api/templates")
async def create_template(data: dict):
    await save_template(data["name"], data["content"])
    return {"status": "ok"}


@app.get("/api/templates")
async def get_templates():
    temps = await list_templates()
    return {"templates": temps}


@app.delete("/api/templates/{id}")
async def remove_template(id: int):
    await delete_template(id)
    return {"status": "ok"}


# ============ 简历管理 ============

@app.post("/api/resume")
async def upload_resume(file: UploadFile = File(...)):
    tmp = os.path.join(tempfile.gettempdir(), file.filename)
    with open(tmp, "wb") as f:
        shutil.copyfileobj(file.file, f)
    info = await parse_resume(tmp)
    os.unlink(tmp)
    if "error" not in info:
        await save_resume_info(info)
    return info


@app.get("/api/resume")
async def fetch_resume():
    info = await get_resume_info()
    return {"resume": info}


# ============ 设置 ============

@app.get("/api/settings")
async def get_settings():
    tone = await get_setting("tone") or "友好"
    provider = await get_setting("ai_provider") or "ollama"
    api_key = await get_setting("openai_api_key") or ""
    base_url = await get_setting("openai_base_url") or "https://api.openai.com/v1"
    model = await get_setting("ai_model") or "gpt-4o-mini"
    return {"tone": tone, "ai_provider": provider, "openai_api_key": api_key,
            "openai_base_url": base_url, "ai_model": model}


@app.post("/api/settings")
async def save_settings(data: dict):
    for k, v in data.items():
        if v:
            await set_setting(k, str(v))
            if k == "openai_api_key":
                os.environ["OPENAI_API_KEY"] = str(v)
            elif k == "openai_base_url":
                os.environ["OPENAI_BASE_URL"] = str(v)
            elif k == "ai_model":
                os.environ["AI_MODEL"] = str(v)
    return {"status": "ok"}


# ============ 统计 ============

@app.get("/api/stats")
async def stats():
    return await get_application_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5678)

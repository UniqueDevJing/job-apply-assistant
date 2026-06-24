"""AI 引擎 - Ollama 优先，OpenAI 兼容 API 回退"""
import os
import json
from backend.db import get_resume_info, get_setting


async def _call_ollama(prompt: str) -> str | None:
    import httpx
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "http://localhost:11434/api/generate",
                json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False}
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
    except Exception:
        pass
    return None


async def _call_openai_compatible(prompt: str) -> str:
    from openai import AsyncOpenAI
    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("AI_MODEL", "gpt-4o-mini")
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    resp = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500,
    )
    return resp.choices[0].message.content or ""


async def generate_reply(hr_message: str, company: str = "", position: str = "") -> list[str]:
    resume = await get_resume_info()
    tone = await get_setting("tone") or "友好"
    resume_text = json.dumps(resume, ensure_ascii=False) if resume else "未上传简历"

    tone_guide = {
        "正式": "用词正式礼貌，使用"您"称呼",
        "友好": "语气自然亲切，像朋友聊天",
        "简洁": "言简意赅，三句话内表达清楚",
    }

    prompt = f"""你是一个求职者的助手，需要帮"我"回复HR的消息。

我的简历信息：
{resume_text}

目标公司：{company or "未指定"}
目标岗位：{position or "未指定"}

HR 的消息：
{hr_message}

请用{tone_guide[tone]}的语气，生成 3 个不同的回复。每个回复独立成段，用 --- 分隔。
注意：
1. 回复要具体，结合我的简历信息
2. 不要写"好的，以下是三个回复"之类的前言
3. 直接给出三个回复内容"""

    try:
        result = await _call_ollama(prompt)
        if not result:
            result = await _call_openai_compatible(prompt)
    except Exception:
        result = await _call_openai_compatible(prompt)

    replies = [r.strip() for r in result.split("---") if r.strip()]
    if len(replies) < 3:
        while len(replies) < 3:
            replies.append(replies[0] if replies else "抱歉，生成失败，请重试。")
    return replies[:3]


async def test_ai_connection(provider: str = "ollama") -> bool:
    if provider == "ollama":
        result = await _call_ollama("回复"好的"")
        return result is not None
    else:
        try:
            await _call_openai_compatible("回复"好的"")
            return True
        except Exception:
            return False

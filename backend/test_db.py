import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db, add_application, list_applications, update_application_status, delete_application
from db import add_message, get_messages, save_template, list_templates, delete_template
from db import save_resume_info, get_resume_info, set_setting, get_setting, close_db

DB = os.path.join(os.path.dirname(__file__), "test_job.db")
os.environ["JOB_DB_PATH"] = DB


async def main():
    import db
    db.DB_PATH = DB
    await init_db()

    # 投递
    aid = await add_application({"company": "测试科技", "position": "前端", "salary": "15-25K", "location": "北京", "status": "待投"})
    assert aid > 0
    apps = await list_applications()
    assert len(apps) >= 1
    await update_application_status(aid, "已投")
    apps = await list_applications(status="已投")
    assert len(apps) == 1

    # 消息
    await add_message(aid, "hr", "你好，看到你的简历，方便聊聊吗？")
    await add_message(aid, "me", "您好，方便！")
    msgs = await get_messages(aid)
    assert len(msgs) == 2

    # 模板
    await save_template("问候", "您好，我是{姓名}，对{岗位}很感兴趣")
    temps = await list_templates()
    assert len(temps) == 1
    await delete_template(temps[0]["id"])

    # 简历
    await save_resume_info({"name": "张三", "skills": "Python,React"})
    info = await get_resume_info()
    assert info["name"] == "张三"

    # 设置
    await set_setting("tone", "正式")
    assert await get_setting("tone") == "正式"

    # 清理
    await delete_application(aid)
    await close_db()
    for f in (DB, DB + "-wal", DB + "-shm"):
        try:
            os.unlink(f)
        except (FileNotFoundError, PermissionError):
            pass
    print("所有数据库测试通过！")

asyncio.run(main())

"""端到端集成测试"""
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB = os.path.join(os.path.dirname(__file__), "test_integration.db")
os.environ["JOB_DB_PATH"] = DB


async def test_flow():
    import db
    db.DB_PATH = DB
    await db.init_db()

    # 模拟用户流程
    aid = await db.add_application({"company": "字节跳动", "position": "前端开发", "salary": "25-40K", "location": "北京"})
    assert aid == 1
    await db.update_application_status(aid, "已投")

    await db.add_message(aid, "hr", "你好，我们收到你的简历，方便聊一下吗？")
    await db.add_message(aid, "me", "您好，方便的！")

    msgs = await db.get_messages(aid)
    assert len(msgs) == 2

    await db.save_template("自我介绍", "您好，我是{姓名}，对{岗位}很感兴趣，我有3年前端开发经验。")
    temps = await db.list_templates()
    assert len(temps) == 1

    await db.save_resume_info({"name": "测试用户", "skills": "React, Vue, TypeScript"})
    info = await db.get_resume_info()
    assert info["name"] == "测试用户"

    await db.set_setting("tone", "简洁")
    assert await db.get_setting("tone") == "简洁"

    stats = await db.get_application_stats()
    assert stats["total"] == 1

    await db.close_db()
    os.unlink(DB)
    print("集成测试全部通过！")


asyncio.run(test_flow())

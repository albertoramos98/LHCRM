import os
import asyncio
import asyncpg
from app.core.config import settings

async def check_pooler(host: str, user: str, password: str, port: int = 6543):
    try:
        conn = await asyncpg.connect(user=user, password=password, host=host, port=port, database="postgres", timeout=5)
        print(f"SUCCESS: Connected to PostgreSQL Pooler ({host}:{port})!")
        await conn.close()
        return True
    except Exception as e:
        print(f"FAIL ({host}:{port}): {e}")
        return False

async def main():
    user = os.environ.get("SUPABASE_POOLER_USER")
    password = os.environ.get("SUPABASE_POOLER_PASSWORD")
    host = os.environ.get("SUPABASE_POOLER_HOST")
    
    if not user or not password or not host:
        print("Set SUPABASE_POOLER_USER, SUPABASE_POOLER_PASSWORD, and SUPABASE_POOLER_HOST environment variables to run pooler checks.")
        return

    for p in [6543, 5432]:
        await check_pooler(host=host, user=user, password=password, port=p)

if __name__ == "__main__":
    asyncio.run(main())

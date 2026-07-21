import asyncio
import asyncpg

async def check(host, port=6543):
    user = "postgres.evkligtiojtsxtqydtog"
    password = "010898dejaneiro!"
    try:
        conn = await asyncpg.connect(user=user, password=password, host=host, port=port, database="postgres", timeout=5)
        print(f"SUCCESS: Connected to Supabase Pooler ({host}:{port})!")
        await conn.close()
        return True
    except Exception as e:
        print(f"FAIL ({host}:{port}): {e}")
        return False

async def main():
    hosts = [
        "aws-0-sa-east-1.pooler.supabase.com",
        "aws-0-us-east-1.pooler.supabase.com",
        "aws-0-us-west-1.pooler.supabase.com",
        "aws-0-eu-west-1.pooler.supabase.com",
        "aws-0-ap-southeast-1.pooler.supabase.com",
        "aws-0-eu-central-1.pooler.supabase.com",
        "aws-0-ca-central-1.pooler.supabase.com",
        "aws-0-ap-northeast-1.pooler.supabase.com",
        "aws-0-us-east-2.pooler.supabase.com",
    ]
    for h in hosts:
        for p in [6543, 5432]:
            if await check(h, p):
                return

if __name__ == "__main__":
    asyncio.run(main())

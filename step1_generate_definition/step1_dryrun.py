import sys
import os
import asyncio
import time
from dotenv import load_dotenv
import random

from mongo.mongo_connector import MongoConnector
from step1_generate_definition.claude_api_wrapper import ClaudeAPIWrapper

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
dotenv_path = os.path.join("env", ".env")

load_dotenv(dotenv_path=dotenv_path)

async def dryrun():
    mongo = MongoConnector()
    claude = ClaudeAPIWrapper()

    query = {
        "content_nouns": {"$exists": True, "$ne": []},
        "situation_definition": {"$exists": False}
    }

    projection = {"content_nouns": 1}
    documents = mongo.fetch_documents(query=query, projection=projection, limit=5)

    if not documents:
        print("⚠️ 조건에 맞는 문서가 없습니다.")
        return

    print(f"🔍 Dry-run 대상 문서 수: {len(documents)}")
    print("=" * 50)

    for doc in documents:
        try:
            start = time.time()
            nouns = doc["content_nouns"]
            if len(nouns) > 8:
                nouns = random.sample(nouns, 8)

            result = await claude.generate_situation_async(nouns)
            duration = time.time() - start
            print(f"[ObjectId: {doc['_id']}]")
            print(f"키워드: {nouns}")
            print(f"→ 생성된 상황정의 문장: {result}")
            print(f"⏱ 처리 시간: {duration:.2f}초")
            print("-" * 50)
        except Exception as e:
            print(f"⚠️ 오류 발생 (id: {doc['_id']}): {e}")

if __name__ == "__main__":
    asyncio.run(dryrun())

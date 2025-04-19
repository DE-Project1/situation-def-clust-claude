# step1_generate.py

from mongo.mongo_connector import MongoConnector
from step1_generate_definition.claude_api_wrapper import ClaudeAPIWrapper
from tqdm import tqdm
import asyncio
import random

from dotenv import load_dotenv
load_dotenv()

async def process_document(cl_wrapper, doc, semaphore, max_retries=3):
    async with semaphore:
        for attempt in range(1, max_retries + 1):
            try:
                nouns = doc["content_nouns"]
                situation = await cl_wrapper.generate_situation_async(nouns)
                return {
                    "_id": doc["_id"],
                    "field": "situation_definition",
                    "value": situation
                }
            except Exception as e:
                print(f"⚠️ 오류 발생 (id: {doc['_id']}, 시도 {attempt}): {e}")
                await asyncio.sleep(2 * attempt + random.random())  # 백오프 + jitter
        return None


async def main(batch_size: int = 32, limit: int = None, concurrency_limit: int = 20):
    mongo = MongoConnector()
    claude = ClaudeAPIWrapper()

    query = {
        "content_nouns": {"$exists": True, "$ne": []},
        "situation_definition": {"$exists": False}
    }
    projection = {"content_nouns": 1}
    documents = mongo.fetch_documents(query=query, projection=projection, limit=limit)

    print(f"🟢 총 대상 문서 수: {len(documents)}")

    semaphore = asyncio.Semaphore(concurrency_limit)

    for i in tqdm(range(0, len(documents), batch_size)):
        batch = documents[i:i + batch_size]

        tasks = [process_document(claude, doc, semaphore) for doc in batch]
        results = await asyncio.gather(*tasks)

        # 유효한 응답만 저장
        updates = [res for res in results if res]

        if updates:
            mongo.bulk_update_fields(updates)

        await asyncio.sleep(0.5)  # Claude 쿼터 회피용

    print("✅ 상황정의 문장 저장 완료!")


if __name__ == "__main__":
    asyncio.run(main())


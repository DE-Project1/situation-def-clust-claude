# step1_generate.py

from mongo.mongo_connector import MongoConnector
from step1_generate_definition.claude_api_wrapper import ClaudeAPIWrapper
from tqdm import tqdm
import asyncio
import random
import time
from collections import deque
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()

# 🔧 초당 요청 수 제한용 RateLimiter 클래스
class RateLimiter:
    def __init__(self, max_rps):
        self.max_rps = max_rps
        self.request_times = deque()

    async def wait(self):
        now = time.time()
        while len(self.request_times) >= self.max_rps:
            if now - self.request_times[0] > 1:
                self.request_times.popleft()
            else:
                await asyncio.sleep(0.01)
                now = time.time()
        self.request_times.append(now)


# 📌 각 문서 비동기 처리 함수
async def process_document(cl_wrapper, doc, semaphore, rate_limiter, max_retries=3):
    async with semaphore:
        for attempt in range(1, max_retries + 1):
            try:
                await rate_limiter.wait()  # 🔒 요청 속도 제한
                nouns = doc["content_nouns"]
                situation = await cl_wrapper.generate_situation_async(nouns)
                return {
                    "_id": doc["_id"],
                    "field": "situation_definition",
                    "value": situation
                }
            except Exception as e:
                print(f"⚠️ 오류 발생 (id: {doc['_id']}, 시도 {attempt}): {e}")
                await asyncio.sleep(2 * attempt + random.random())
        return None


# 🎯 메인 처리 루프
async def main(batch_size: int = 32, limit: int = None, concurrency_limit: int = 30, max_rps: int = 15):
    mongo = MongoConnector()
    claude = ClaudeAPIWrapper()

    query = {
        "content_nouns": {"$exists": True, "$ne": []},
        "situation_definition": {"$exists": False}
    }
    projection = {"content_nouns": 1}
    documents = mongo.fetch_documents(query=query, projection=projection, limit=limit)

    total_docs = len(documents)
    print(f"🟢 총 대상 문서 수: {total_docs}")

    semaphore = asyncio.Semaphore(concurrency_limit)
    rate_limiter = RateLimiter(max_rps=max_rps)
    stats = deque()
    start_all = time.time()

    for batch_idx in tqdm(range(0, total_docs, batch_size)):
        batch = documents[batch_idx:batch_idx + batch_size]
        start_time = time.time()

        tasks = [process_document(claude, doc, semaphore, rate_limiter) for doc in batch]
        results = await asyncio.gather(*tasks)

        duration = time.time() - start_time
        updates = [res for res in results if res]

        if updates:
            mongo.bulk_update_fields(updates)

        # 처리 통계 저장
        stats.append((datetime.now(), len(updates), duration))

        # 최근 10분만 유지
        ten_minutes_ago = datetime.now() - timedelta(minutes=10)
        while stats and stats[0][0] < ten_minutes_ago:
            stats.popleft()

        # ETA 출력 (5배치마다)
        if (batch_idx // batch_size + 1) % 5 == 0:
            total_processed = sum(s[1] for s in stats)
            total_duration = sum(s[2] for s in stats)

            if total_processed > 0:
                speed = total_processed / total_duration
                remaining = total_docs - batch_idx - batch_size
                eta_minutes = (remaining / speed) / 60
                print(f"⏳ ETA: 약 {eta_minutes:.2f}분 (최근 10분 기준)")

    print("✅ 상황정의 문장 저장 완료!")
    total_elapsed = time.time() - start_all
    print(f"⏱ 총 소요 시간: {total_elapsed / 60:.2f}분")


if __name__ == "__main__":
    asyncio.run(main())


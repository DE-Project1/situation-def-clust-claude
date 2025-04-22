import os
from dotenv import load_dotenv
from pymongo import MongoClient

# .env 파일 경로
dotenv_path = os.path.join("env", ".env")
load_dotenv(dotenv_path=dotenv_path)

# MongoDB 연결 정보
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("DB_COLLECTION")

print("MONGO_URI:", MONGO_URI)
print("DB_NAME:", DB_NAME)
print("COLLECTION_NAME:", COLLECTION_NAME)

# Mongo 연결
client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COLLECTION_NAME]

# ✅ 조건 없이 상위 5개 문서 찾기
documents = list(collection.find().limit(5))

# 결과 출력
if documents:
    print(f"🔍 총 {len(documents)}개 문서가 검색되었습니다:")
    for doc in documents:
        print(f"- _id: {doc['_id']}")
        print(f"  content_nouns: {doc.get('content_nouns')}")
else:
    print("⚠️ 문서가 없습니다.")



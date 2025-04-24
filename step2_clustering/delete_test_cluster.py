# test 용으로 100개만 clustering했던 거 삭제하는 코드입니다.
# 다른 step에서는 돌리지 않으시도록 주의해주세요

from pymongo import MongoClient
from dotenv import load_dotenv
import os

# .env에서 연결 정보 불러오기
load_dotenv()
uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")
collection_name = os.getenv("DB_COLLECTION")

client = MongoClient(uri)
collection = client[db_name][collection_name]

# situation_cluster 필드 제거
result = collection.update_many(
    {"situation_cluster": {"$exists": True}},
    {"$unset": {"situation_cluster": ""}}
)

print(f"🧹 삭제된 문서 수: {result.modified_count}")

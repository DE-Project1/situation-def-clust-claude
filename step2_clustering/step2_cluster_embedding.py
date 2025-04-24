# step2_cluster_embedding.py
# 상황정의 임베딩하고 해당 값을 json으로 저장하는 과정입니다

from mongo.mongo_connector import MongoConnector
from step2_clustering.embedding_kosbert import KoBERTEmbedder
import os

from dotenv import load_dotenv
load_dotenv()

def main(batch_size: int = 1000, start_batch: int = 0):
    mongo = MongoConnector()
    embedder = KoBERTEmbedder()

    total_fetched = 0
    batch_index = start_batch

    os.makedirs("embedding_data", exist_ok=True)  # ✅ 폴더 생성

    while True:
        query = {
            "situation_definition": {"$exists": True, "$ne": None},
        }
        projection = {"situation_definition": 1}
        documents = mongo.fetch_documents(query=query,
                                          projection=projection,
                                          limit=batch_size,
                                          skip=batch_index * batch_size,
                                          sort=[("_id", 1)])

        if not documents:
            print("✅ 모든 문서를 처리했습니다.")
            break

        print(f"🟢 총 클러스터링 대상 문서 수: {len(documents)}")

        doc_ids = [str(doc["_id"]) for doc in documents]
        situation_sentences = [doc["situation_definition"] for doc in documents]

        print(f"📦 배치 {batch_index}: 시작 ID = {doc_ids[0]}")

        # 1. 임베딩
        print("🔄 임베딩 중...")
        embeddings = embedder.encode(situation_sentences,show_progress_bar=True)

        # 2. 임베딩 저장
        embedding_dict = {doc_id: vec.tolist() for doc_id, vec in zip(doc_ids, embeddings)}
        import json

        file_path = f"embedding_data/embedding_batch_{batch_index}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(embedding_dict, f)
        print(f"💾 임베딩 결과 저장 완료: {file_path}")

        total_fetched += len(documents)
        batch_index += 1

        print(f"🎉 총 {total_fetched}건 임베딩 완료!")

if __name__ == "__main__":
    main()




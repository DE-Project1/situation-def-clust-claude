# step2_cluster_clustering.py

import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from bson import ObjectId
from mongo.mongo_connector import MongoConnector
from dotenv import load_dotenv

load_dotenv()

# 1. merged_vectors json 파일에서 벡터 로딩
def load_vectors_from_merged_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        merged = json.load(f)
    vector_ids = list(merged.keys())
    vectors = np.array(list(merged.values()))
    return vector_ids, vectors

# 2. 클러스터링 결과를 MongoDB에 저장
def upload_cluster_results_to_mongo(cluster_map : dict):
    mongo = MongoConnector()
    updates = []
    for _id, cluster in cluster_map.items():
        try:
            updates.append({
                "_id": ObjectId(_id),
                "field": "situation_cluster",
                "value": int(cluster)
            })
        except Exception as e:
            print(f"❗ ObjectId 변환 실패 (ID: {_id}) → {e}")

    if updates:
        mongo.bulk_update_fields(updates)
        print(f"✅ MongoDB에 클러스터 결과 {len(updates)}건 업데이트 완료")
    else:
        print("⚠️ 업데이트할 항목이 없습니다.")

# 3. 전체 실행 흐름
if __name__ == "__main__":
    # (1) 로딩
    print("🚀 merged_vectors.json 로딩 중...")
    ids, embeddings = load_vectors_from_merged_json("./step2_clustering/merged_vectors.json")
    print(f"✅ 벡터 수: {len(ids)}")

    # (2) KMeans 클러스터링
    print("🔍 KMeans 클러스터링 중...")
    kmeans = KMeans(n_clusters=20, random_state=42, n_init="auto")
    labels = kmeans.fit_predict(embeddings)

    id_to_cluster = {id_: int(cluster) for id_, cluster in zip(ids, labels)}

    # (3) 품질 평가
    print(f"📉 관성(Inertia): {kmeans.inertia_:.2f}")
    sil_score = silhouette_score(embeddings, labels)
    print(f"📊 실루엣 점수: {sil_score:.4f}")

    # (4) MongoDB 업로드
    print("⬆️ MongoDB에 클러스터 결과 업로드 중...")
    upload_cluster_results_to_mongo(id_to_cluster)

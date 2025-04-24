# new_merged_vectors.npy 바탕으로 로컬에서 클러스터링 진행하고 결과를 출력해보는 파일입니다.


import json
import numpy as np
from sklearn.cluster import KMeans
from bson import ObjectId
from collections import defaultdict
from mongo.mongo_connector import MongoConnector
from dotenv import load_dotenv

load_dotenv()

# 1. npy 벡터 + ID json 불러오기
def load_vectors_from_npy_and_ids(npy_path: str, id_path: str):
    vectors = np.load(npy_path)
    with open(id_path, 'r', encoding='utf-8') as f:
        ids = json.load(f)
    return ids, vectors

# 2. MongoDB에서 situation_definition 가져오기 (직접 fetch_documents 사용)
def fetch_situation_definitions(ids):
    mongo = MongoConnector()
    object_ids = []
    for _id in ids:
        try:
            object_ids.append(ObjectId(_id))
        except Exception as e:
            print(f"❗ ObjectId 변환 실패: {_id} → {e}")
    if not object_ids:
        return {}

    documents = mongo.fetch_documents(
        query={"_id": {"$in": object_ids}},
        projection={"situation_definition": 1}
    )

    id_to_definition = {
        str(doc["_id"]): doc.get("situation_definition")
        for doc in documents if "situation_definition" in doc
    }
    return id_to_definition

# 3. 클러스터별 상황정의 출력
def print_clustered_sentences(id_to_cluster, id_to_definition, sample_n=3):
    clusters = defaultdict(list)
    for _id, cluster in id_to_cluster.items():
        sentence = id_to_definition.get(_id)
        if sentence:
            clusters[cluster].append(sentence)

    print(f"\n📊 클러스터링 결과 요약 (클러스터 수: {len(clusters)})\n")
    for cluster_id in sorted(clusters.keys()):
        print(f"🔹 클러스터 {cluster_id} ({len(clusters[cluster_id])} 문장)")
        for sentence in clusters[cluster_id][:sample_n]:
            print(f"   - {sentence}")
        print()

# 4. 전체 실행 흐름
if __name__ == "__main__":
    print("🚀 벡터 및 ID 로딩 중...")
    ids, embeddings = load_vectors_from_npy_and_ids("new_merged_vectors.npy", "ids.json")
    print(f"✅ 로딩 완료: {len(ids)}개")

    print("🔍 KMeans 클러스터링 중 (n_clusters=20)...")
    kmeans = KMeans(n_clusters=20, random_state=42, n_init="auto")
    labels = kmeans.fit_predict(embeddings)
    id_to_cluster = {id_: int(cluster) for id_, cluster in zip(ids, labels)}

    print("🧲 MongoDB에서 상황정의 불러오는 중...")
    id_to_definition = fetch_situation_definitions(ids)

    print_clustered_sentences(id_to_cluster, id_to_definition, sample_n=50)

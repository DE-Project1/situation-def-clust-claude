import json
import numpy as np
from collections import defaultdict
from sklearn.cluster import KMeans
from bson import ObjectId
from mongo.mongo_connector import MongoConnector
from dotenv import load_dotenv

load_dotenv()

#1. merged_vectors json 파일에서 벡터 로딩
def load_vectors_from_merged_json(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        merged = json.load(f)
    ids = list(merged.keys())
    vectors = np.array(list(merged.values()))
    return ids, vectors


#2. MongoDB에서 상황정의 조회
def fetch_definitions_from_mongo(ids):
    mongo = MongoConnector()
    try:
        object_ids = [ObjectId(_id) for _id in ids]
    except Exception as e:
        print("❗ ObjectId 변환 실패:", e)
        return {}

    query = {"_id": {"$in": object_ids}}
    projection = {"situation_definition": 1}
    docs = mongo.fetch_documents(query=query, projection=projection)

    id_to_definition = {}
    for doc in docs:
        if "_id" in doc and "situation_definition" in doc:
            id_to_definition[str(doc["_id"])] = doc["situation_definition"]

    print(f"🧾 MongoDB에서 조회된 상황정의 수: {len(id_to_definition)}개")
    return id_to_definition


#3. 클러스터링 및 결과 출력
if __name__ == "__main__":
    print("🚀 merged_vectors.json 로딩 중...")
    ids, embeddings = load_vectors_from_merged_json("merged_vectors.json")
    print(f"✅ 벡터 수: {len(ids)}")

    print("🔍 KMeans 클러스터링 중...")
    kmeans = KMeans(n_clusters=40, random_state=42, n_init="auto")
    labels = kmeans.fit_predict(embeddings)

    id_to_cluster = {id_: int(cluster) for id_, cluster in zip(ids, labels)}

    print("🌐 MongoDB에서 상황정의 조회 중...")
    id_to_definition = fetch_definitions_from_mongo(ids)

    clusters = defaultdict(list)
    for _id, cluster in id_to_cluster.items():
        sentence = id_to_definition.get(_id)
        if sentence:
            clusters[cluster].append(sentence)

    print("\n📊 클러스터별 상황정의:")
    for cluster_id in sorted(clusters.keys()):
        print(f"\n🟢 클러스터 {cluster_id} (총 {len(clusters[cluster_id])}개 문장):")
        for i, sentence in enumerate(clusters[cluster_id], start=1):
            print(f"  {i}. {sentence}")

# step2_cluster.py

from mongo.mongo_connector import MongoConnector
from step2_clustering.embedding_kosbert import KoBERTEmbedder
from sklearn.cluster import KMeans

from dotenv import load_dotenv
load_dotenv()

def main(n_clusters: int = 20, limit: int = None):
    mongo = MongoConnector()

    query = {
        "situation_definition": {"$exists": True, "$ne": None},
        "situation_cluster": {"$exists": False}
    }
    projection = {"situation_definition": 1}
    documents = mongo.fetch_documents(query=query, projection=projection, limit=limit)

    print(f"🟢 총 클러스터링 대상 문서 수: {len(documents)}")

    situation_sentences = [doc["situation_definition"] for doc in documents]

    # 1. 임베딩
    embedder = KoBERTEmbedder()
    print("🔄 임베딩 중...")
    embeddings = embedder.encode(situation_sentences)

    # 2. 클러스터링
    print(f"🔍 KMeans 클러스터링 시작 (클러스터 수: {n_clusters})")
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    cluster_labels = kmeans.fit_predict(embeddings)

    # 3. MongoDB에 저장
    updates = []
    for doc, label in zip(documents, cluster_labels):
        updates.append({
            "_id": doc["_id"],
            "field": "situation_cluster",
            "value": int(label)
        })

    print("📝 클러스터 ID 저장 중...")
    mongo.bulk_update_fields(updates)
    print("✅ 클러스터링 완료!")


if __name__ == "__main__":
    main()

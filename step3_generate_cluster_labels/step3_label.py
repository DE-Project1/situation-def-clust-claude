import random
import asyncio
from mongo.mongo_connector import MongoConnector
from generate_labels import generate_cluster_label

async def generate_labels_for_clusters_with_sampling(mongo):
    cluster_ids = mongo.collection.distinct("situation_cluster")
    labels = {}
    for cluster_id in cluster_ids:
        docs = mongo.fetch_documents(
            query={"situation_cluster": cluster_id},
            projection={"situation_definition": 1}
        )
        definitions_docs = [doc for doc in docs if "situation_definition" in doc]
        if not definitions_docs:
            continue
        sample_size = max(1, len(definitions_docs) // 2)
        sampled_docs = random.sample(definitions_docs, sample_size)
        definitions = [doc["situation_definition"] for doc in sampled_docs]
        label = await generate_cluster_label(definitions)
        labels[cluster_id] = label
    return labels

async def update_cluster_names(mongo, labels):
    for cluster_id, label in labels.items():
        docs = mongo.fetch_documents(
            query={"situation_cluster": cluster_id},
            projection={"_id": 1}
        )
        updates = [
            {"_id": doc["_id"], "field": "cluster_name", "value": label}
            for doc in docs
        ]
        mongo.bulk_update_fields(updates)

async def main():
    mongo = MongoConnector()
    labels = await generate_labels_for_clusters_with_sampling(mongo)
    await update_cluster_names(mongo, labels)
    print("✅ 샘플링 기반 대표 상황명 저장 완료")

if __name__ == "__main__":
    asyncio.run(main())
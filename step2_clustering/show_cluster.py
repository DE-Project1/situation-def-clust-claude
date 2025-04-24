# cluster 별로 상황정의 뽑아보려고 만든 코드입니다

from mongo.mongo_connector import MongoConnector
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()

def show_cluster_definitions():
    mongo = MongoConnector()

    # 1. 클러스터링된 문서만 불러오기
    query = {
        "situation_cluster": {"$exists": True},
        "situation_definition": {"$exists": True}
    }
    projection = {
        "situation_definition": 1,
        "situation_cluster": 1
    }
    documents = mongo.fetch_documents(query=query, projection=projection)

    print(f"🔍 불러온 문서 수: {len(documents)}")

    # 2. 클러스터별로 문장 묶기
    clusters = defaultdict(list)
    for doc in documents:
        cluster_id = doc["situation_cluster"]
        sentence = doc["situation_definition"]
        clusters[cluster_id].append(sentence)

    # 3. 출력
    for cluster_id in sorted(clusters.keys()):
        print(f"\n🟢 클러스터 {cluster_id} (총 {len(clusters[cluster_id])}개 문장):")
        for i, sentence in enumerate(clusters[cluster_id], start=1):
            print(f"  {i}. {sentence}")

if __name__ == "__main__":
    show_cluster_definitions()

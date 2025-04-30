import os
import random
import time
from pymongo import MongoClient
from claude_api_wrapper import ClaudeAPIWrapper
from dotenv import load_dotenv

# .env 로드
load_dotenv(dotenv_path=os.path.join("env", ".env"))

# MongoDB 연결
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["de25proejct1DB"]
collection = db["reviews"]

# Claude API 초기화
claude = ClaudeAPIWrapper()

# 결과 저장 디렉토리
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_dir = os.path.join(project_root, "step3_generate_cluster_labels")


# 클러스터 ID 목록 (0 ~ 19) - 기본값: 모든 클러스터
all_cluster_ids = list(range(20))  # 모든 클러스터에 대해 진행

# 특정 클러스터만 지정할 때 사용
specified_cluster_ids = []

# 지정된 클러스터만 처리하고, 비어있으면 모든 클러스터 처리
cluster_ids = specified_cluster_ids if specified_cluster_ids else all_cluster_ids

# 모든 클러스터에 대해 반복
all_labels = {}

for cluster_id in cluster_ids:
    print(f"클러스터 {cluster_id} 처리 시작...")

    # 해당 클러스터에 속하는 문서들 가져오기
    docs = list(collection.find({"situation_cluster": cluster_id}, {"situation_definition": 1}))
    print(f"  총 {len(docs)}개의 상황정의 문서 발견")

    # 1/4 랜덤 샘플링
    sampled_docs = random.sample(docs, len(docs) // 4) if len(docs) > 4 else docs
    print(f"  샘플링된 {len(sampled_docs)}개 상황정의 사용")

    # situation_definition 리스트로 변환
    situation_definitions = [doc["situation_definition"] for doc in sampled_docs]

    labels_for_this_cluster = []

    # 1000개씩 나눠서 처리
    for i in range(0, len(situation_definitions), 1000):
        batch = situation_definitions[i:i + 1000]
        print(f"{i}번부터 {i + len(batch)}번까지 API 요청")

        label = claude.generate_label(batch)  # claude API 호출
        print(f"생성된 대표 상황정의: {label}")

        labels_for_this_cluster.append(label)

        print("1분 대기 중...")
        time.sleep(60)  # 1분 대기

    # 클러스터별 라벨 저장
    txt_filename = os.path.join(output_dir, f"cluster_{cluster_id}.txt")
    with open(txt_filename, "w", encoding="utf-8") as f:
        for label in labels_for_this_cluster:
            f.write(label + "\n")

    print(f"💾 클러스터 {cluster_id} 라벨 {len(labels_for_this_cluster)}개 저장 완료! ➡ {txt_filename}")

    all_labels[cluster_id] = labels_for_this_cluster
    print(f"클러스터 {cluster_id} 처리 완료!\n")

print("🌟 전체 클러스터 처리 완료!")


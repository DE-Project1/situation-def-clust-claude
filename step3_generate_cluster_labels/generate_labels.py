import numpy as np
import random
from step3_generate_cluster_labels.claude_api_wrapper import generate_cluster_label
from mongo.mongo_connector import get_collection

def generate_label_for_cluster(cluster_id: int, dryrun=False, sample_size=100):
    # 상황정의 리스트 로드
    file_path = f"data/cluster_defs/cluster_{cluster_id}.npy"
    try:
        situation_defs = np.load(file_path, allow_pickle=True).tolist()
    except FileNotFoundError:
        print(f"[Cluster {cluster_id}] 파일 없음: {file_path}")
        return None

    if not situation_defs:
        print(f"[Cluster {cluster_id}] 비어 있음")
        return None

    # 샘플링
    sample_defs = random.sample(situation_defs, min(len(situation_defs), sample_size))

    # Claude 호출
    label = generate_cluster_label(sample_defs, dryrun=dryrun)

    # MongoDB 업데이트
    if not dryrun:
        col = get_collection()
        result = col.update_many({"situation_cluster": cluster_id}, {"$set": {"cluster_name": label}})
        print(f"[Cluster {cluster_id}] {result.modified_count}개 문서 업데이트 완료")

    return label

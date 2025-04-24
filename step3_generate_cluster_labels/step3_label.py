from step3_generate_cluster_labels.generate_label import generate_label_for_cluster

if __name__ == "__main__":
    for cluster_id in range(20):  # 0 ~ 19 클러스터
        print(f"\n===== Cluster {cluster_id} =====")
        label = generate_label_for_cluster(cluster_id, dryrun=True)  # 최초엔 dryrun=True
        print(f"▶ 생성된 대표 라벨: {label}")

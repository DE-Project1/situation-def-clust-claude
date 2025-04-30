from mongo.mongo_connector import MongoConnector

# cluster_mapping 정의
cluster_mapping = {
    0: "스트레스 해소를 위해 매운 음식이 땡길 때",
    1: "혼밥에 부담없는 맛집을 찾을 때",
    2: "식사 메뉴에 고기가 빠지면 아쉬운 사람일 때",
    3: "배달이나 포장이 편리한 식당이 필요할 때",
    4: "곱창과 다양한 내장요리를 맛있게 즐기고 싶을 때",
    5: "뜨끈한 국물로 몸을 녹이고 싶을 때",
    6: "친구나 가족과 함께 소중한 시간을 보내고 싶을 때",
    7: "친절한 서비스로 기분 좋은 식사시간을 원할 때",
    8: "집밥처럼 정성가득한 반찬을 맛보고 싶을 때",
    9: "정통 일본 요리를 음미하고 싶을 때",
    10: "맛있는 안주가 있는 술집을 찾을 때",
    11: "고기의 맛과 질에 만족하는 식사를 하고 싶을 때",
    12: "가족들과 주말에 방문할 맛집을 찾을 때",
    13: "데이트 코스로 양식을 대접하고 싶을 때",
    14: "특별한 날에 만족할 만한 서비스를 원할 때",
    15: "다양한 중식 메뉴가 있는 분위기 좋은 중식당을 찾을 때",
    16: "친구들과 편하게 치맥을 즐기고 싶을 때",
    17: "가성비 좋은 식당에서 지인들과 모임을 가지고 싶을 때",
    18: "편안한 분위기에서 여유롭게 식사하며 기분 전환하고 싶을 때",
    19: "신선한 수산물 요리를 괜찮은 가격에 즐기고 싶을 때"
}

# MongoDB 연결 설정
mongo_connector = MongoConnector()


# situation_cluster에 해당하는 cluster_name을 추가하는 함수
def update_cluster_name():
    for cluster, cluster_name in cluster_mapping.items():
        # situation_cluster가 cluster인 문서에 cluster_name을 추가
        documents = mongo_connector.fetch_documents({"situation_cluster": cluster})
        updates = []

        for doc in documents:
            updates.append({
                "_id": doc["_id"],
                "field": "cluster_name",
                "value": cluster_name
            })

        # 일괄 업데이트
        if updates:
            mongo_connector.bulk_update_fields(updates)
            print(f"Updated cluster_name for situation_cluster {cluster}")


# 클러스터 이름 업데이트 함수 호출
update_cluster_name()

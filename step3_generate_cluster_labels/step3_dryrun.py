# step3 dryrun 돌려보는 파일입니다.
# 클러스터 하나(18번으로 했음)에서 상황정의 다 긁어오고
# 그 중에 100개 랜덤으로 뽑아서 LLM에 넣어주었습니다.
# 프롬프트는 claude_api_wrapper에서 확인할 수 있습니다.
# 결과로 나온 대표문장 하나가 파일로 저장됩니다.

import random
import asyncio
from mongo.mongo_connector import MongoConnector
from generate_labels import generate_cluster_label

from dotenv import load_dotenv
load_dotenv()

async def dryrun_generate_label_for_one_cluster(mongo, cluster_id):
    # 1. 해당 클러스터 문서 가져오기
    docs = mongo.fetch_documents(
        query={"situation_cluster": cluster_id},
        projection={"situation_definition": 1}
    )
    definitions_docs = [doc for doc in docs if "situation_definition" in doc]

    if not definitions_docs:
        print(f"⚠️ 클러스터 {cluster_id}에는 situation_definition이 없습니다.")
        return

    # 2. 상황정의 100개 샘플링
    sample_size = min(100, len(definitions_docs))
    sampled_docs = random.sample(definitions_docs, sample_size)
    definitions = [doc["situation_definition"] for doc in sampled_docs]

    # 3. Claude API 호출해서 대표 상황정의 생성
    try:
        label = await generate_cluster_label(definitions)
    except Exception as e:
        print(f"❌ Claude API 호출 실패: {e}")
        return

    # 4. 결과 출력
    print(f"\n=== Cluster {cluster_id} 대표 상황정의 생성 완료 ===\n")
    return (cluster_id, label)  # 오직 결과만 반환! 파일 저장 X


async def main():
    mongo = MongoConnector()
    output_file = "dryrun_result_all.txt"

    # 첫 번째 클러스터 시작 전에 파일 초기화
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=== Dryrun 결과 모음 ===\n\n")

    for cluster_id in range(20):
        try:
            result = await dryrun_generate_label_for_one_cluster(mongo, cluster_id)
            if result is not None:
                cluster_id, label = result
                with open(output_file, "a", encoding="utf-8") as f:
                    f.write(f"### Cluster {cluster_id} 대표 상황정의 ###\n")
                    f.write(label + "\n\n")
            else:
                print(f"⚪ Cluster {cluster_id}: 저장할 label 없음")
        except Exception as e:
            print(f"❌ 클러스터 {cluster_id} dryrun 중 오류 발생: {e}")
            continue  # 에러가 나도 다음 클러스터로 넘어가기


if __name__ == "__main__":
    asyncio.run(main())

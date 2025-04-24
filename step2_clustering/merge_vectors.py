import os
import json
import numpy as np
from tqdm import tqdm

def load_some_vectors_from_json(folder_path: str, max_files: int = None):
    vectors = []
    ids = []
    file_count = 0
    for filename in tqdm(os.listdir(folder_path), desc="📂 JSON 파일 일부 로딩 중"):
        if filename.endswith(".json"):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                doc_dict = json.load(f)
                for _id, vector in doc_dict.items():
                    ids.append(_id)
                    vectors.append(vector)
            file_count += 1
            if max_files is not None and file_count >= max_files:
                break
    return ids, np.array(vectors)


def main(json_folder: str = "./embedding_data",
         merged_vector_file: str = "merged_vectors.json",
         file_limit: int = None):
    print("🚀 JSON 벡터 일부 로딩 중...")
    ids, embeddings = load_some_vectors_from_json(json_folder, max_files=file_limit)
    print(f"✅ 로딩된 문서 수: {len(ids)}")


    # JSON에 통합된 임베딩 저장
    merged_vectors = {id_: vector.tolist() for id_, vector in zip(ids, embeddings)}
    with open(merged_vector_file, "w", encoding="utf-8") as f:
        json.dump(merged_vectors, f, ensure_ascii=False, indent=2)
    print(f"📦 벡터 통합 JSON 저장 완료 → {merged_vector_file}")


if __name__ == "__main__":
    main()

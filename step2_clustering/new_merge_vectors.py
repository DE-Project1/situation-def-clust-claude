# 기존에 batch size=1000으로 해서 임베딩했던 파일들 npy로 병합하는 코드입니다.

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
    return ids, np.array(vectors, dtype=np.float32)

def main(json_folder: str = "./embedding_data",
         npy_vector_file: str = "new_merged_vectors.npy",
         id_file: str = "ids.json",
         file_limit: int = None):
    print("🚀 JSON 벡터 일부 로딩 중...")
    ids, embeddings = load_some_vectors_from_json(json_folder, max_files=file_limit)
    print(f"✅ 로딩된 문서 수: {len(ids)}")
    print(f"📐 벡터 shape: {embeddings.shape}")

    # .npy로 벡터 저장
    np.save(npy_vector_file, embeddings)
    print(f"💾 벡터 저장 완료 → {npy_vector_file}")

    # ID는 JSON으로 따로 저장
    with open(id_file, "w", encoding="utf-8") as f:
        json.dump(ids, f, ensure_ascii=False, indent=2)
    print(f"🆔 ID 저장 완료 → {id_file}")

if __name__ == "__main__":
    main()


import numpy as np

vectors = np.load("new_merged_vectors.npy")
print(vectors.shape)
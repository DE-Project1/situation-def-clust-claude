from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import torch

class KoBERTEmbedder:
    def __init__(self, model_name: str = "jhgan/ko-sbert-nli"):
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=device)

    def encode(self, texts: Union[str, List[str]], show_progress_bar: bool = False) -> np.ndarray:
        """
        주어진 문장 또는 문장 리스트를 Ko-SBERT 임베딩 벡터로 변환

        Args:
            texts: str 또는 str의 리스트 (상황정의 문장)
            show_progress_bar: 변환 중 진행상황 표시 여부

        Returns:
            np.ndarray: (1, 768) 또는 (N, 768) 차원의 벡터 배열
        """
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=show_progress_bar
        )

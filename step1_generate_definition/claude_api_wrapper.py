# claude_api_wrapper.py

import os
import httpx
from typing import List
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join("env", ".env"))

class ClaudeAPIWrapper:
    def __init__(self, model: str = "claude-3-haiku-20240307"):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/messages"

        if not self.api_key:
            raise ValueError("⚠️ ANTHROPIC_API_KEY is missing in environment variables.")

        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

    @staticmethod
    def build_prompt(content_nouns: List[str]) -> str:
        prompt = (
            "다음 키워드로 유추되는 음식점 추천 상황을 한 문장으로 간결하게 말해줘.\n"
            "문장은 '~할 때'로 끝내. 문장은 하나만 출력해.\n"
            f"키워드: {', '.join(content_nouns)}\n"
            "상황 정의:"
        )
        return prompt

    async def generate_situation_async(self, content_nouns: List[str]) -> str:
        prompt = self.build_prompt(content_nouns)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": self.model,
                    "max_tokens": 100,
                    "temperature": 0.3,
                    "top_p" : 0.7,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )

        if response.status_code != 200:
            raise Exception(f"API 호출 실패: {response.status_code}, {response.text}")

        content = response.json()
        if not content.get("content") or not isinstance(content["content"], list):
            raise Exception(f"API 응답 형식 오류: {content}")

        result = content["content"][0].get("text", "").strip()

        # 로그 출력
        return result







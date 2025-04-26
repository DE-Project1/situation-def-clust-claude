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
    def build_prompt(definitions: List[str]) -> str:
        prompt = (
            "아래는 한 그룹에 속하는 상황 정의 문장들입니다.\n"
            "이 문장들을 집약해 대표되는 상황 명칭을 하나의 짧은 문장으로 만들어주세요.\n"
        )
        for i, definition in enumerate(definitions, 1):
            prompt += f"{i}. {definition}\n"
        prompt += "\n대표 명칭:"
        return prompt

    async def generate_cluster_label_async(self, definitions: List[str]) -> str:
        prompt = self.build_prompt(definitions)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": self.model,
                    "max_tokens": 64,
                    "temperature": 0.2,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )

        if response.status_code != 200:
            raise Exception(f"API 호출 실패: {response.status_code}, {response.text}")

        content = response.json()
        # Anthropic 최신 API는 'content' 필드가 리스트임
        if not content.get("content") or not isinstance(content["content"], list):
            raise Exception(f"API 응답 형식 오류: {content}")

        result = content["content"][0].get("text", "").strip()
        return result

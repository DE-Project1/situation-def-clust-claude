import os
from anthropic import Anthropic
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv(dotenv_path=os.path.join("env", ".env"))

class ClaudeAPIWrapper:
    def __init__(self, model: str = "claude-3-haiku-20240307"):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("⚠️ ANTHROPIC_API_KEY is missing in environment variables.")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    def generate_label(self, situation_definitions_batch):
        joined_text = "\n".join(f"- {s}" for s in situation_definitions_batch)

        prompt = (
            "다음 문장들을 보고 사용자가 어떤 상황일 때 해당 음식점을 방문하는 것이 좋을지, 하나의 주제 문장을 만들어줘.\n"
            "\n"
            "조건:\n"
            "- 문장은 반드시 '~할 때'로 끝내.\n"
            "- 음식 종류나 메뉴 위주로 작성하지마. 대신 기분, 추천 상황, 목적 같은 특징은 살려서 표현해줘.\n"
            "- 구체적인 욕구나 활동(예: 스트레스 풀고 싶을 때, 기름진 음식을 즐기고 싶을 때)로 표현해줘.\n"
            "- 문장 속 단어를 그대로 나열하는 식이 아니었으면 좋겠어.\n"
            "- 하나의 공통된 패턴과 의미를 반영해.\n"
            "\n"
            "예시:\n"
            "- 친구랑 수다 떨며 편하게 모이고 싶을 때\n"
            "- 비 오는 날 따뜻한 국물 요리를 즐기고 싶을 때\n"
            "\n"
            f"{joined_text}\n\n대표 문장:"
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=256,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.content[0].text.strip()


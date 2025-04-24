import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_cluster_label(situations: list[str], dryrun=False) -> str:
    prompt_body = "\n".join(f"- {s}" for s in situations)
    prompt = (
        f"{anthropic.HUMAN_PROMPT} 다음은 유사한 상황 정의들입니다:\n"
        f"{prompt_body}\n\n"
        f"위 내용을 하나의 대표 상황 정의 문장으로 요약해 주세요.{anthropic.AI_PROMPT}"
    )

    if dryrun:
        print("=== DRYRUN PROMPT ===")
        print(prompt)
        return "예시 대표 상황 문장"

    response = client.completions.create(
        model="claude-3-haiku-20240307",
        prompt=prompt,
        max_tokens_to_sample=200,
        temperature=0.5
    )
    return response.completion.strip()

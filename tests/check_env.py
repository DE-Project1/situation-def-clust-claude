import os
from dotenv import load_dotenv

dotenv_path = os.path.join("env", ".env")

load_dotenv(dotenv_path=dotenv_path)

# 1. .env 파일 존재 여부 확인
if not os.path.exists(dotenv_path):
    print(f"❌ .env 파일이 존재하지 않습니다: {dotenv_path}")
else:
    print(f"✅ .env 파일 발견됨: {dotenv_path}")

    # 2. .env 로드
    load_dotenv(dotenv_path=dotenv_path)

    # 3. 환경 변수 확인
    required_vars = ["MONGO_URI", "DB_NAME", "DB_COLLECTION"]
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"🔹 {var} = {value}")
        else:
            print(f"❌ {var} 이(가) 설정되지 않았습니다.")
            all_set = False

    if all_set:
        print("🎉 모든 환경 변수가 올바르게 설정되어 있습니다!")
    else:
        print("⚠️ 누락된 환경 변수가 있어 MongoConnector 사용에 문제가 생길 수 있습니다.")

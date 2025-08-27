"""
간단한 Service Server 시뮬레이터
- 기존 샘플 데이터를 랜덤으로 반환
- 최소한의 MSA 통신 시뮬레이션
"""

import json
import random
import time
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="간단한 Service Server 시뮬레이터")

class ServiceData(BaseModel):
    doc_input: str
    collection_id: str
    collection_name: str
    collection_memo: str
    user_id: str

# 샘플 데이터 로드
def load_samples():
    samples = []
    sample_dir = Path(".")
    for file_path in sample_dir.glob("sample_input_*.json"):
        with open(file_path, 'r', encoding='utf-8') as f:
            samples.append(json.load(f))
    return samples

samples = load_samples()

@app.get("/")
def root():
    return {"message": "Service Server 시뮬레이터", "samples": len(samples)}

@app.get("/data", response_model=ServiceData)
def get_data():
    """랜덤 샘플 데이터 반환"""
    if not samples:
        # 기본 데이터
        return ServiceData(
            doc_input="테스트 문서 내용입니다.",
            collection_id=f"{datetime.now().strftime('%y%m%d')}_00000001",
            collection_name="TEST_NEWS",
            collection_memo="테스트용 메모",
            user_id="ko_00000001"
        )
    
    # 기존 샘플에서 랜덤 선택
    sample = random.choice(samples).copy()
    
    # ID 변경
    sample["user_id"] = f"ko_{random.randint(1, 9999):08d}"
    sample["collection_id"] = f"{datetime.now().strftime('%y%m%d')}_{random.randint(1, 9999):08d}"
    
    return ServiceData(**sample)

if __name__ == "__main__":
    import uvicorn
    print("🚀 간단한 Service Server 시뮬레이터 시작...")
    print("📡 URL: http://localhost:8001")
    print("📖 데이터 API: http://localhost:8001/data")
    uvicorn.run(app, host="0.0.0.0", port=8001) 
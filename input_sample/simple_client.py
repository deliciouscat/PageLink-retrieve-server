"""
간단한 테스트 클라이언트
"""

import requests
import asyncio
import aiohttp
import argparse
import json
from pathlib import Path

def load_sample_data(sample_num):
    """지정된 샘플 파일 로드"""
    # 현재 스크립트와 같은 디렉토리에서 샘플 파일 찾기
    current_dir = Path(__file__).parent
    sample_file = current_dir / f"sample_input_{sample_num}.json"
    
    if not sample_file.exists():
        print(f"❌ 샘플 파일을 찾을 수 없습니다: {sample_file}")
        return None
    
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"📂 샘플 파일 로드: sample_input_{sample_num}.json")
            print(f"   📋 컬렉션: {data['collection_name']}")
            print(f"   👤 사용자: {data['user_id']}")
            return data
    except Exception as e:
        print(f"❌ 샘플 파일 로드 오류: {e}")
        return None

def test_sync():
    """동기 테스트 (Service Server에서 랜덤 데이터)"""
    print("🧪 동기 테스트...")
    try:
        response = requests.get("http://localhost:8001/data")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 성공: {data['collection_name']} / {data['user_id']}")
            return data
        else:
            print(f"❌ 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 오류: {e}")
    return None

async def test_async():
    """비동기 테스트"""
    print("🧪 비동기 테스트...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get("http://localhost:8001/data") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ 성공: {data['collection_name']} / {data['user_id']}")
                    return data
                else:
                    print(f"❌ 실패: {response.status}")
        except Exception as e:
            print(f"❌ 오류: {e}")
    return None

async def send_to_retrieve_server(data):
    """Retrieve Server로 전송 테스트"""
    print("📤 Retrieve Server로 전송...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("http://localhost:8000/process", json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ 처리 완료: {result['status']}")
                    return result
                else:
                    print(f"❌ 실패: {response.status}")
        except Exception as e:
            print(f"❌ 오류: {e}")
    return None

async def main():
    parser = argparse.ArgumentParser(description='PageLink Retrieve Server 테스트 클라이언트')
    parser.add_argument('--sample', type=int, choices=[1, 2], 
                       help='사용할 샘플 파일 번호 (1 또는 2). 지정하지 않으면 Service Server에서 랜덤 데이터 사용')
    
    args = parser.parse_args()
    
    if args.sample:
        # 지정된 샘플 파일 사용
        print(f"🎯 샘플 {args.sample} 모드")
        data = load_sample_data(args.sample)
        if not data:
            return
        
        # Retrieve Server로 직접 전송
        await send_to_retrieve_server(data)
    else:
        # 기존 방식: Service Server 연동
        print("🔄 Service Server 연동 모드")
        
        # 1. 동기 테스트
        data = test_sync()
        
        # 2. 비동기 테스트  
        await test_async()
        
        # 3. Retrieve Server 연동 테스트
        if data:
            await send_to_retrieve_server(data)

if __name__ == "__main__":
    asyncio.run(main())

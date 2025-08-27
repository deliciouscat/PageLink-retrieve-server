"""
문서 인덱싱 모듈 - 더미 구현
"""
import asyncio
import random


async def doc_indexing(data_instance):
    """
    문서 인덱싱 함수 (더미 구현)
    doc_input을 받아서 질문 리스트를 생성
    """
    print(f"🔍 [doc_indexing] 시작 - User: {data_instance.user_id}")
    
    # 1-2초 딜레이 시뮬레이션
    delay = random.uniform(1.0, 2.0)
    await asyncio.sleep(delay)
    
    # 더미 질문 리스트 생성
    questions = [
        f"{data_instance.collection_name}에 대한 질문 1",
        f"{data_instance.collection_name}에 대한 질문 2", 
        f"{data_instance.collection_name}에 대한 질문 3"
    ]
    
    print(f"✅ [doc_indexing] 완료 ({delay:.1f}초) - User: {data_instance.user_id}")
    return questions
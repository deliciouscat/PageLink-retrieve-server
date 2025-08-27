"""
컬렉션 쿼리 확장 모듈 - 더미 구현
"""
import asyncio
import random


async def expand_collection_query(data_instance):
    """
    컬렉션 쿼리 확장 함수 (더미 구현)
    doc_summary 결과를 받아서 컬렉션 질문을 생성
    doc_summary -> expand_collection_query 순서 의존성
    """
    print(f"🔄 [expand_collection_query] 시작 - User: {data_instance.user_id}")
    
    # 1-2초 딜레이 시뮬레이션
    delay = random.uniform(1.0, 2.0)
    await asyncio.sleep(delay)
    
    # doc_summarized_new가 있는지 확인 (의존성 체크)
    if hasattr(data_instance, 'doc_summarized_new') and data_instance.doc_summarized_new:
        base_text = data_instance.doc_summarized_new
    else:
        base_text = data_instance.doc_input
    
    # 더미 컬렉션 질문 생성
    collection_questions = [
        f"{data_instance.collection_name} 컬렉션 관련 질문 1",
        f"{data_instance.collection_name} 컬렉션 관련 질문 2",
        f"확장된 쿼리: {base_text[:30]}..."
    ]
    
    print(f"✅ [expand_collection_query] 완료 ({delay:.1f}초) - User: {data_instance.user_id}")
    return collection_questions
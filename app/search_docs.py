"""
문서 검색 모듈 - 더미 구현
"""
import asyncio
import random


async def search_docs(data_instance):
    """
    문서 검색 함수 (더미 구현)
    expand_collection_query 결과를 받아서 관련 문서를 검색
    expand_collection_query -> search_docs 순서 의존성
    """
    print(f"🔎 [search_docs] 시작 - User: {data_instance.user_id}")
    
    # 1-2초 딜레이 시뮬레이션  
    delay = random.uniform(1.0, 2.0)
    await asyncio.sleep(delay)
    
    # collection_question이 있는지 확인 (의존성 체크)
    if hasattr(data_instance, 'collection_question') and data_instance.collection_question:
        query_base = f"기반 쿼리: {len(data_instance.collection_question)}개"
    else:
        query_base = "기본 검색"
    
    # 더미 검색 결과 생성
    retrieved_docs = [
        f"검색된 문서 1 - {data_instance.collection_name}",
        f"검색된 문서 2 - {query_base}", 
        f"검색된 문서 3 - {data_instance.user_id} 관련"
    ]
    
    print(f"✅ [search_docs] 완료 ({delay:.1f}초) - User: {data_instance.user_id}")
    return retrieved_docs

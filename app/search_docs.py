"""
문서 검색 모듈
"""
import asyncio
from app.retrieve.api_search.natural_search import from_openrouter

async def search_single_question(question: str):
    """단일 질문에 대한 검색 수행"""
    try:
        # from_openrouter가 동기 함수이므로 executor에서 실행
        loop = asyncio.get_event_loop()
        search_result = await loop.run_in_executor(None, from_openrouter, question, True)
        return search_result.urls
    except Exception as e:
        print(f"⚠️ [search_docs] 검색 실패: {question} - {str(e)}")
        return []

async def search_docs(data_instance):
    """
    문서 검색 함수
    expand_collection_query 결과를 받아서 관련 문서를 검색
    expand_collection_query -> search_docs 순서 의존성
    """
    print(f"🔎 [search_docs] 시작 - User: {data_instance.user_id}")
    
    # collection_question이 있는지 확인 (의존성 체크)
    if not (hasattr(data_instance, 'collection_question') and data_instance.collection_question):
        print(f"⚠️ [search_docs] collection_question이 없음 - User: {data_instance.user_id}")
        return []
    
    # 모든 질문을 병렬로 검색 수행
    questions = [q.get('question') for q in data_instance.collection_question.get('questions')]

    # 질문 너무 많은데, 핵심적이고 좋은 질문으로 추려서 검색 ㄱ?

    search_tasks = [
        search_single_question(question) 
        for question in questions
    ]
    
    # 병렬 실행
    results = await asyncio.gather(*search_tasks)
    
    # 모든 결과를 하나의 리스트로 합치고 중복 제거
    all_urls = []
    for urls in results:
        all_urls.extend(urls)
    
    unique_urls = list(set(all_urls))
    
    print(f"✅ [search_docs] 완료 - User: {data_instance.user_id}, 결과: {len(unique_urls)}개")
    return unique_urls

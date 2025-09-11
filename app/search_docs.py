"""
문서 검색 모듈
"""
import asyncio
import os
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field
from typing import List

from app.retrieve.api_search.natural_search import from_openrouter
from app.retrieve.api_search.keyword_search import from_ddgs
from app.llm.inference import structured_inference

# 현재 파일의 디렉토리를 기준으로 templates 폴더 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'llm')
env = Environment(loader=FileSystemLoader(template_dir))
    
class QueriesResponse(BaseModel):
    """여러 질문들을 담는 응답 모델"""
    queries: List[str] = Field(description="생성된 쿼리들의 리스트", min_items=2, max_items=6)

async def question_merging(question_list: List[str]):
    """
    문서 인덱싱 함수 - pydantic-ai 구조화된 출력 사용
    doc_input을 받아서 질문 리스트를 생성
    """
    print(f"🔍 [question_merging] 시작 - User: {question_list}")
    
    template = env.get_template('prompts/question_merging_250911.jinja')
    prompt = template.render(question_list=question_list)
    
    # 구조화된 출력을 위한 새로운 inference 함수 사용
    result = await structured_inference(
        prompt=prompt,
        # structured output은 제한된 모델만 가능:
        # - gpt-4 계열, gemini-2.5 계열
        # - 불가능한 모델: gpt-5 계열, grok-3 계열
        #model_name="google/gemini-2.5-flash-lite",
        model_name="openai/gpt-4.1-mini",
        model_settings={
            "temperature": 0.8,
            "max_tokens": 1000,
        },
        output_type=QueriesResponse  # 구조화된 출력 타입 지정
    )

    # result.output이 이미 QuestionsResponse 객체임
    queries_response = result.output
    
    print(f"✅ [question_merging] 완료 - User: {question_list}")

    
    return {
        "queries": queries_response.queries
    }

async def search_single_question(question: str):
    """단일 질문에 대한 검색 수행"""
    try:
        # 검색 엔진 선택: 아래 중 하나의 주석을 해제하여 사용
        loop = asyncio.get_event_loop()
        
        # 옵션 1: 자연어 검색 (Perplexity/OpenRouter 기반)
        #search_result = await loop.run_in_executor(None, from_openrouter, question, True)
        
        # 옵션 2: 키워드 검색 (DuckDuckGo 기반)
        search_result = await loop.run_in_executor(None, from_ddgs, question, True)
        
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

    # 질문 목록을 쿼리 목록으로 변환
    queries_result = await question_merging(questions)
    queries = queries_result["queries"]
    print(f"🔍 [search_docs] 쿼리 목록: {queries}")
    
    search_tasks = [
        search_single_question(query) 
        for query in queries
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

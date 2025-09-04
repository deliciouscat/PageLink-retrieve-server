"""
컬렉션 쿼리 확장 모듈
"""
import os
import asyncio
import random
from app.llm.inference import inference#structured_inference
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field
from typing import List
import json


# 현재 파일의 디렉토리를 기준으로 templates 폴더 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'llm')
env = Environment(loader=FileSystemLoader(template_dir))

class Question(BaseModel):
    """생성된 질문을 나타내는 모델"""
    question: str = Field(description="문서 내용을 기반으로 생성된 질문")
    #answer: str = Field(description="생성된 질문의 답변")
    

class QuestionsResponse(BaseModel):
    """여러 질문들을 담는 응답 모델"""
    questions: List[Question] = Field(description="생성된 질문들의 리스트", min_items=2, max_items=6)

async def expand_collection_query(data_instance):
    """
    문서 인덱싱 함수 - pydantic-ai 구조화된 출력 사용
    doc_input을 받아서 질문 리스트를 생성
    """
    print(f"🔍 [expand_collection_query] 시작 - User: {data_instance.user_id}")
    
    template = env.get_template('prompts/expand_collection_query_250903.jinja')
    # doc_summaries 구성
    data_instance.doc_summarized.append({"summary": data_instance.doc_summarized_new, "summary_id": data_instance.doc_summarized_new_id})
    doc_summaries_joined = "\n------\n".join([summary["summary"] for summary in data_instance.doc_summarized])
    # 여기까진 확실히 됨
    prompt = template.render(doc_summaries=doc_summaries_joined, collection_memo=data_instance.collection_memo)
    
    # 구조화된 출력을 위한 새로운 inference 함수 사용
    result = await inference(
        prompt=prompt,
        # structured output은 제한된 모델만 가능:
        # - gpt-4 계열, gemini-2.5 계열
        # - 불가능한 모델: gpt-5 계열, grok-3 계열
        #model_name="google/gemini-2.5-pro",
        #model_name="x-ai/grok-3-mini",
        model_name="qwen/qwen3-235b-a22b-thinking-2507",
        model_settings={
            "temperature": 0.7,
            "max_tokens": 5000,
        },
        system_prompt=None,
        #output_type=QuestionsResponse  # 구조화된 출력 타입 지정
    )
    questions_response = json.loads(result.output)
    #print("🔍🔍questions_response🔍🔍")
    #print(questions_response)
    print(f"✅ [doc_indexing] 완료 - User: {data_instance.user_id}")

    return questions_response

    # structured output 사용 시 코드
    #return {
    #    "questions": [q.model_dump() for q in questions_response.questions]
    #}
    
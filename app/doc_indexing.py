"""
문서 인덱싱 모듈 - pydantic-ai 구조화된 출력 사용
"""
import os
import asyncio
import random
from app.llm.inference import structured_inference
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel, Field
from typing import List


# 현재 파일의 디렉토리를 기준으로 templates 폴더 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'llm')
env = Environment(loader=FileSystemLoader(template_dir))

# 기존 str_to_json 함수는 parser 모듈로 이동
# from app.llm.parser import json_parser as str_to_json  # 하위 호환성

class Question(BaseModel):
    """생성된 질문을 나타내는 모델"""
    question: str = Field(description="문서 내용을 기반으로 생성된 질문")
    answer: str = Field(description="생성된 질문의 답변")
    

class QuestionsResponse(BaseModel):
    """여러 질문들을 담는 응답 모델"""
    questions: List[Question] = Field(description="생성된 질문들의 리스트", min_items=2, max_items=6)

async def doc_indexing(data_instance):
    """
    문서 인덱싱 함수 - pydantic-ai 구조화된 출력 사용
    doc_input을 받아서 질문 리스트를 생성
    """
    print(f"🔍 [doc_indexing] 시작 - User: {data_instance.user_id}")
    
    template = env.get_template('prompts/doc_indexing_250830.jinja')
    system_prompt = template.render(doc_input=data_instance.doc_input, memopad=data_instance.collection_memo)
    
    # 구조화된 출력을 위한 새로운 inference 함수 사용
    result = await structured_inference(
        prompt=data_instance.doc_input,
        # structured output은 제한된 모델만 가능:
        # - gpt-4 계열, gemini-2.5 계열
        # - 불가능한 모델: gpt-5 계열, grok-3 계열
        model_name="google/gemini-2.5-flash-lite",
        #model_name="openai/gpt-4.1-nano",
        model_settings={
            "temperature": 0.75,
            "max_tokens": 1000,
        },
        system_prompt=system_prompt,
        output_type=QuestionsResponse  # 구조화된 출력 타입 지정
    )
    
    # raw result 출력
    print(result)
    
    # result.output이 이미 QuestionsResponse 객체임
    questions_response = result.output
    
    print(f"✅ [doc_indexing] 완료 - User: {data_instance.user_id}")

    
    return {
        "questions": [q.model_dump() for q in questions_response.questions]
    }
    


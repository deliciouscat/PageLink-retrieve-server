"""
문서 인덱싱 모듈 - pydantic-ai 구조화된 출력 사용
"""
import os
import asyncio
import random
from app.llm.inference import structured_inference, inference
from app.llm.parser import json_parser, safe_json_parser
from app.data_model import QuestionsResponse
from jinja2 import Environment, FileSystemLoader
import json
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
    
    try:
        # 구조화된 출력을 위한 새로운 inference 함수 사용
        result = await structured_inference(
            prompt=data_instance.doc_input,
            model_name="x-ai/grok-3-mini",
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
        
    except Exception as e:
        print(f"⚠️ [doc_indexing] 구조화된 출력 실패, 기존 방식으로 fallback: {e}")
        
        # fallback: 기존 텍스트 기반 방식
        result = await inference(
            prompt=data_instance.doc_input,
            model_name="x-ai/grok-3-mini",
            model_settings={
                "temperature": 0.75,
                "max_tokens": 1000,
            },
            system_prompt=system_prompt
        )
        
        # 안전한 JSON 파싱 사용
        questions = safe_json_parser(result.output, QuestionsResponse)
        
        if questions:
            print(f"✅ [doc_indexing] Fallback 완료 - User: {data_instance.user_id}")
            return {
                "questions": [q.model_dump() for q in questions.questions]
            }
        else:
            # 마지막 fallback: 기본 JSON 파싱
            basic_questions = safe_json_parser(result.output)
            print(f"⚠️ [doc_indexing] 기본 파싱으로 완료 - User: {data_instance.user_id}")
            return basic_questions or {"questions": [], "total_count": 0}

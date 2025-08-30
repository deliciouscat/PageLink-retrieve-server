"""
문서 요약 모듈
"""
import os
import asyncio
import random
from app.llm.inference import inference
from jinja2 import Environment, FileSystemLoader


# 현재 파일의 디렉토리를 기준으로 templates 폴더 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'llm')
env = Environment(loader=FileSystemLoader(template_dir))

async def doc_summary(data_instance):
    """
    제어 변수:
    모델, configs, system_prompt
    """
    print(f"📝 [doc_summary] 시작 - User: {data_instance.user_id}")
    # 템플릿 렌더링
    template = env.get_template('prompts/doc_summary_250828.jinja')
    system_prompt = template.render(doc_input=data_instance.doc_input)
    
    result = await inference(
        prompt=data_instance.doc_input,  # prompt와 system_prompt 순서 수정
        model_name="google/gemma-3-27b-it",
        model_settings={
            "temperature": 0.6,
            "max_tokens": 1000,
        },
        system_prompt=system_prompt
    )
    
    summary = result.output
    print(f"✅ [doc_summary] 완료 - User: {data_instance.user_id}")
    return summary
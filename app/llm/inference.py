# 필요 기능:
# 1. 모델 별 라우팅
# 2. API 키 관리
import os
from pydantic_ai import Agent
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic import BaseModel
from typing import Type, TypeVar, Any

'''
이미 완성된 프롬프트를 받아서 인퍼런스

# input
model_name: str
prompt: str

# output

'''

async def inference(prompt: str, model_name: str, model_settings: dict, system_prompt: str):
    model = OpenAIChatModel(
        model_name,
        provider=OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY")),
    )
    agent = Agent(
        model,
        model_settings=model_settings,
        system_prompt=system_prompt,
    )
    result = await agent.run(prompt)
    return result


async def structured_inference(
    prompt: str, 
    model_name: str, 
    model_settings: dict, 
    system_prompt: str,
    output_type: Type[BaseModel]
) -> Any:
    """구조화된 출력을 위한 새로운 inference 함수"""
    model = OpenAIChatModel(
        model_name,
        provider=OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY")),
    )
    agent = Agent(
        model,
        model_settings=model_settings,
        system_prompt=system_prompt,
        output_type=output_type  # 구조화된 출력 타입 지정
    )
    result = await agent.run(prompt)
    return result